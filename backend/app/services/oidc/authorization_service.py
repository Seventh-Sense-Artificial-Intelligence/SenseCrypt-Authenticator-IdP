import hashlib
import base64
import logging
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.models.product.authorization_code import AuthorizationCode

logger = logging.getLogger(__name__)


async def create_authorization_code(
    db: AsyncSession,
    client_id: str,
    email: str,
    redirect_uri: str,
    scope: str,
    nonce: str | None,
    code_challenge: str | None,
    code_challenge_method: str | None,
    state: str | None,
) -> str:
    settings = get_settings()
    code = secrets.token_urlsafe(48)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.OIDC_AUTH_CODE_EXPIRE_MINUTES
    )

    auth_code = AuthorizationCode(
        code=code,
        client_id=client_id,
        email=email,
        redirect_uri=redirect_uri,
        scope=scope,
        nonce=nonce,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        state=state,
        expires_at=expires_at,
    )
    db.add(auth_code)
    await db.commit()
    return code


async def exchange_authorization_code(
    db: AsyncSession,
    code: str,
    client_id: str,
    redirect_uri: str,
    code_verifier: str | None,
) -> AuthorizationCode | None:
    result = await db.execute(
        select(AuthorizationCode).where(AuthorizationCode.code == code)
    )
    auth_code = result.scalar_one_or_none()
    if not auth_code:
        logger.error("Auth code not found in DB for code=%s", code[:20])
        return None

    # Validate not used
    if auth_code.is_used:
        logger.error("Auth code already used")
        return None

    # Validate not expired
    expires = auth_code.expires_at if auth_code.expires_at.tzinfo else auth_code.expires_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires:
        logger.error("Auth code expired: %s", expires)
        return None

    # Validate client_id matches
    if auth_code.client_id != client_id:
        logger.error("client_id mismatch: stored=%s, received=%s", auth_code.client_id, client_id)
        return None

    # Validate redirect_uri matches
    if auth_code.redirect_uri != redirect_uri:
        logger.error("redirect_uri mismatch: stored=%r, received=%r", auth_code.redirect_uri, redirect_uri)
        return None

    # Validate PKCE code_verifier if code_challenge was stored
    if auth_code.code_challenge:
        if not code_verifier:
            logger.error("PKCE: code_verifier missing but code_challenge was stored")
            return None
        if auth_code.code_challenge_method == "S256":
            digest = hashlib.sha256(code_verifier.encode()).digest()
            expected = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
            if expected != auth_code.code_challenge:
                logger.error("PKCE S256 mismatch: expected=%s, stored=%s", expected, auth_code.code_challenge)
                return None
        else:
            # plain method
            if code_verifier != auth_code.code_challenge:
                logger.error("PKCE plain mismatch")
                return None

    # Mark as used
    auth_code.is_used = True
    await db.commit()
    await db.refresh(auth_code)
    return auth_code
