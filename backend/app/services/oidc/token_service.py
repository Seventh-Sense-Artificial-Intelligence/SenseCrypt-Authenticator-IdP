import hashlib
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import Settings
from app.models.product.refresh_token import OIDCRefreshToken
from app.services.oidc.keys import sign_jwt, get_public_key


def create_id_token(
    email: str,
    client_id: str,
    nonce: str | None,
    scopes: set[str],
    settings: Settings,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict = {
        "iss": settings.OIDC_ISSUER_URL,
        "sub": email,
        "aud": client_id,
        "exp": now + timedelta(minutes=settings.OIDC_ID_TOKEN_EXPIRE_MINUTES),
        "iat": now,
    }
    if nonce:
        payload["nonce"] = nonce
    if "email" in scopes:
        payload["email"] = email
        payload["email_verified"] = True
    if "profile" in scopes:
        payload["name"] = email
    return sign_jwt(payload)


def create_oidc_access_token(
    email: str,
    client_id: str,
    scopes: set[str],
    settings: Settings,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "iss": settings.OIDC_ISSUER_URL,
        "sub": email,
        "aud": client_id,
        "exp": now + timedelta(minutes=settings.OIDC_ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now,
        "scope": " ".join(sorted(scopes)),
    }
    return sign_jwt(payload)


async def create_refresh_token(
    db: AsyncSession, email: str, client_id: str, scope: str
) -> str:
    raw_token = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)

    refresh_token = OIDCRefreshToken(
        token_hash=token_hash,
        client_id=client_id,
        email=email,
        scope=scope,
        expires_at=expires_at,
    )
    db.add(refresh_token)
    await db.commit()
    return raw_token


def validate_access_token(token: str) -> dict | None:
    try:
        public_key = get_public_key()
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload
    except jwt.PyJWTError:
        return None
