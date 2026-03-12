import hashlib
import io
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone

import qrcode
import qrcode.image.svg
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.models.product.auth_challenge import AuthChallenge
from app.services.oidc.authorization_service import create_authorization_code

logger = logging.getLogger(__name__)


def compute_purpose_id(client_id: str, redirect_uri: str) -> str:
    return hashlib.sha256((client_id + redirect_uri).encode()).hexdigest()


def generate_qr_svg(data: str) -> str:
    img = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage)
    buf = io.BytesIO()
    img.save(buf)
    return buf.getvalue().decode()


async def create_challenge(
    db: AsyncSession,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str | None,
    nonce: str | None,
    code_challenge: str | None,
    code_challenge_method: str | None,
    response_type: str,
    login_hint: str | None,
    settings: Settings | None = None,
) -> AuthChallenge:
    if settings is None:
        settings = get_settings()

    challenge_nonce = secrets.token_urlsafe(48)
    purpose_id = compute_purpose_id(client_id, redirect_uri)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.AUTH_CHALLENGE_EXPIRE_MINUTES
    )

    challenge = AuthChallenge(
        challenge_nonce=challenge_nonce,
        purpose_id=purpose_id,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        state=state,
        nonce=nonce,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        response_type=response_type,
        login_hint=login_hint,
        status="pending",
        expires_at=expires_at,
    )
    db.add(challenge)
    await db.commit()
    await db.refresh(challenge)
    return challenge


def build_qr_data(challenge: AuthChallenge, settings: Settings | None = None) -> str:
    if settings is None:
        settings = get_settings()
    payload = {
        "v": 1,
        "challenge": challenge.challenge_nonce,
        "purpose_id": challenge.purpose_id,
        "identity": challenge.login_hint or "",
        "url": f"{settings.BASE_URL}/challenge/{challenge.id}/submit",
    }
    return json.dumps(payload, separators=(",", ":"))


async def get_challenge_status(db: AsyncSession, challenge_id: str) -> dict | None:
    result = await db.execute(
        select(AuthChallenge).where(AuthChallenge.id == challenge_id)
    )
    challenge = result.scalar_one_or_none()
    if not challenge:
        return None

    # Check expiry
    expires = (
        challenge.expires_at
        if challenge.expires_at.tzinfo
        else challenge.expires_at.replace(tzinfo=timezone.utc)
    )
    if challenge.status == "pending" and datetime.now(timezone.utc) > expires:
        challenge.status = "expired"
        await db.commit()

    resp: dict = {"status": challenge.status}
    if challenge.status == "completed" and challenge.redirect_url:
        resp["redirect_url"] = challenge.redirect_url
    return resp


async def _complete_challenge(
    db: AsyncSession,
    challenge: AuthChallenge,
    email: str,
) -> str:
    code = await create_authorization_code(
        db=db,
        client_id=challenge.client_id,
        email=email,
        redirect_uri=challenge.redirect_uri,
        scope=challenge.scope,
        nonce=challenge.nonce,
        code_challenge=challenge.code_challenge,
        code_challenge_method=challenge.code_challenge_method,
        state=challenge.state,
    )

    redirect_url = f"{challenge.redirect_uri}?code={code}"
    if challenge.state:
        redirect_url += f"&state={challenge.state}"

    challenge.status = "completed"
    challenge.redirect_url = redirect_url
    await db.commit()
    return redirect_url


async def submit_challenge(
    db: AsyncSession,
    challenge_id: str,
    signed_challenge: str,
    certificate_pem: str,
    settings: Settings | None = None,
) -> dict:
    if settings is None:
        settings = get_settings()

    result = await db.execute(
        select(AuthChallenge).where(AuthChallenge.id == challenge_id)
    )
    challenge = result.scalar_one_or_none()
    if not challenge:
        return {"error": "Challenge not found", "status_code": 404}

    if challenge.status != "pending":
        return {"error": f"Challenge is {challenge.status}", "status_code": 400}

    expires = (
        challenge.expires_at
        if challenge.expires_at.tzinfo
        else challenge.expires_at.replace(tzinfo=timezone.utc)
    )
    if datetime.now(timezone.utc) > expires:
        challenge.status = "expired"
        await db.commit()
        return {"error": "Challenge expired", "status_code": 400}

    if not settings.CA_PUBLIC_KEY_PEM:
        return {"error": "CA public key not configured", "status_code": 500}

    # Verify certificate against CA and signature against challenge
    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding, utils

        # Load CA public key
        ca_public_key = serialization.load_pem_public_key(
            settings.CA_PUBLIC_KEY_PEM.encode()
        )

        # Load submitted certificate
        cert = x509.load_pem_x509_certificate(certificate_pem.encode())

        # Verify cert was signed by CA
        ca_public_key.verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )

        # Verify the signed challenge against the cert's public key
        cert_public_key = cert.public_key()
        import base64
        signature_bytes = base64.b64decode(signed_challenge)
        cert_public_key.verify(
            signature_bytes,
            challenge.challenge_nonce.encode(),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )

        # Extract email from certificate subject or SAN
        email = None
        try:
            san = cert.extensions.get_extension_for_class(
                x509.SubjectAlternativeNames
            )
            emails = san.value.get_values_for_type(x509.RFC822Name)
            if emails:
                email = emails[0]
        except x509.ExtensionNotFound:
            pass

        if not email:
            for attr in cert.subject:
                if attr.oid == x509.oid.NameOID.EMAIL_ADDRESS:
                    email = attr.value
                    break

        if not email:
            return {"error": "No email found in certificate", "status_code": 400}

    except Exception as e:
        logger.error("Certificate verification failed: %s", e)
        return {"error": "Certificate verification failed", "status_code": 400}

    redirect_url = await _complete_challenge(db, challenge, email)
    return {"redirect_url": redirect_url}


async def submit_challenge_demo(
    db: AsyncSession,
    challenge_id: str,
    settings: Settings | None = None,
) -> dict:
    if settings is None:
        settings = get_settings()

    if not settings.DEMO_MODE:
        return {"error": "Not found", "status_code": 404}

    result = await db.execute(
        select(AuthChallenge).where(AuthChallenge.id == challenge_id)
    )
    challenge = result.scalar_one_or_none()
    if not challenge:
        return {"error": "Challenge not found", "status_code": 404}

    if challenge.status != "pending":
        return {"error": f"Challenge is {challenge.status}", "status_code": 400}

    expires = (
        challenge.expires_at
        if challenge.expires_at.tzinfo
        else challenge.expires_at.replace(tzinfo=timezone.utc)
    )
    if datetime.now(timezone.utc) > expires:
        challenge.status = "expired"
        await db.commit()
        return {"error": "Challenge expired", "status_code": 400}

    if not challenge.login_hint:
        return {"error": "No login_hint on challenge", "status_code": 400}

    redirect_url = await _complete_challenge(db, challenge, challenge.login_hint)
    return {"redirect_url": redirect_url}


async def refresh_challenge(
    db: AsyncSession,
    challenge_id: str,
    settings: Settings | None = None,
) -> dict:
    if settings is None:
        settings = get_settings()

    result = await db.execute(
        select(AuthChallenge).where(AuthChallenge.id == challenge_id)
    )
    old = result.scalar_one_or_none()
    if not old:
        return {"error": "Challenge not found", "status_code": 404}

    # Only allow refresh of expired or pending challenges
    expires = (
        old.expires_at
        if old.expires_at.tzinfo
        else old.expires_at.replace(tzinfo=timezone.utc)
    )
    if old.status == "pending" and datetime.now(timezone.utc) > expires:
        old.status = "expired"

    if old.status not in ("expired", "pending"):
        return {"error": f"Challenge is {old.status}, cannot refresh", "status_code": 400}

    # Create new challenge with same OIDC params
    new_challenge = await create_challenge(
        db=db,
        client_id=old.client_id,
        redirect_uri=old.redirect_uri,
        scope=old.scope,
        state=old.state,
        nonce=old.nonce,
        code_challenge=old.code_challenge,
        code_challenge_method=old.code_challenge_method,
        response_type=old.response_type,
        login_hint=old.login_hint,
        settings=settings,
    )

    # Delete old challenge
    await db.delete(old)
    await db.commit()

    # Generate new QR
    qr_data = build_qr_data(new_challenge, settings)
    qr_svg = generate_qr_svg(qr_data)

    return {
        "challenge_id": new_challenge.id,
        "qr_svg": qr_svg,
        "expire_seconds": settings.AUTH_CHALLENGE_EXPIRE_MINUTES * 60,
    }
