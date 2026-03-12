import base64
import hashlib
from fastapi import APIRouter, Depends, Form, Header
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.database import get_db
from app.config import get_settings
from app.models.product.refresh_token import OIDCRefreshToken
from app.services.product.application_service import (
    get_application_by_client_id,
    verify_client_credentials,
)
from app.services.oidc.authorization_service import exchange_authorization_code
from app.services.oidc.token_service import (
    create_id_token,
    create_oidc_access_token,
    create_refresh_token,
)

router = APIRouter()


def _parse_basic_auth(authorization: str | None) -> tuple[str | None, str | None]:
    if not authorization or not authorization.startswith("Basic "):
        return None, None
    try:
        decoded = base64.b64decode(authorization[6:]).decode()
        client_id, client_secret = decoded.split(":", 1)
        return client_id, client_secret
    except Exception:
        return None, None


@router.post("/token")
async def token_endpoint(
    grant_type: str = Form(...),
    code: str | None = Form(default=None),
    redirect_uri: str | None = Form(default=None),
    code_verifier: str | None = Form(default=None),
    client_id: str | None = Form(default=None),
    client_secret: str | None = Form(default=None),
    refresh_token: str | None = Form(default=None),
    scope: str | None = Form(default=None),
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()

    # Extract client credentials from Basic auth or form body
    basic_client_id, basic_client_secret = _parse_basic_auth(authorization)
    effective_client_id = basic_client_id or client_id
    effective_client_secret = basic_client_secret or client_secret

    if grant_type == "authorization_code":
        return await _handle_authorization_code(
            db=db,
            settings=settings,
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
            client_id=effective_client_id,
            client_secret=effective_client_secret,
        )
    elif grant_type == "refresh_token":
        return await _handle_refresh_token(
            db=db,
            settings=settings,
            refresh_token_value=refresh_token,
            client_id=effective_client_id,
            client_secret=effective_client_secret,
        )
    elif grant_type == "client_credentials":
        return await _handle_client_credentials(
            db=db,
            settings=settings,
            client_id=effective_client_id,
            client_secret=effective_client_secret,
            scope=scope,
        )
    else:
        return JSONResponse(
            status_code=400,
            content={"error": "unsupported_grant_type"},
        )


async def _handle_authorization_code(
    db: AsyncSession,
    settings,
    code: str | None,
    redirect_uri: str | None,
    code_verifier: str | None,
    client_id: str | None,
    client_secret: str | None,
):
    if not code or not redirect_uri or not client_id:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_request"},
        )

    # Exchange the authorization code
    auth_code = await exchange_authorization_code(
        db=db,
        code=code,
        client_id=client_id,
        redirect_uri=redirect_uri,
        code_verifier=code_verifier,
    )
    if not auth_code:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_grant"},
        )

    # Verify client credentials (if secret provided)
    if client_secret:
        app = await verify_client_credentials(db, client_id, client_secret)
        if not app:
            return JSONResponse(
                status_code=401,
                content={"error": "invalid_client"},
            )
    else:
        # For public clients (SPA/native) that don't have a secret
        app = await get_application_by_client_id(db, client_id)
        if not app or not app.is_active:
            return JSONResponse(
                status_code=401,
                content={"error": "invalid_client"},
            )

    scopes = set(auth_code.scope.split()) if auth_code.scope else {"openid"}

    id_token = create_id_token(
        email=auth_code.email,
        client_id=client_id,
        nonce=auth_code.nonce,
        scopes=scopes,
        settings=settings,
    )
    access_token = create_oidc_access_token(
        email=auth_code.email,
        client_id=client_id,
        scopes=scopes,
        settings=settings,
    )
    rt = await create_refresh_token(
        db=db,
        email=auth_code.email,
        client_id=client_id,
        scope=auth_code.scope or "openid",
    )

    return JSONResponse(
        content={
            "access_token": access_token,
            "id_token": id_token,
            "refresh_token": rt,
            "token_type": "Bearer",
            "expires_in": settings.OIDC_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "scope": auth_code.scope or "openid",
        }
    )


async def _handle_refresh_token(
    db: AsyncSession,
    settings,
    refresh_token_value: str | None,
    client_id: str | None,
    client_secret: str | None,
):
    if not refresh_token_value or not client_id:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_request"},
        )

    # Verify client credentials
    if client_secret:
        app = await verify_client_credentials(db, client_id, client_secret)
        if not app:
            return JSONResponse(
                status_code=401,
                content={"error": "invalid_client"},
            )
    else:
        app = await get_application_by_client_id(db, client_id)
        if not app or not app.is_active:
            return JSONResponse(
                status_code=401,
                content={"error": "invalid_client"},
            )

    # Look up refresh token in DB by SHA-256 hash
    token_hash = hashlib.sha256(refresh_token_value.encode()).hexdigest()
    result = await db.execute(
        select(OIDCRefreshToken).where(
            OIDCRefreshToken.client_id == client_id,
            OIDCRefreshToken.token_hash == token_hash,
            OIDCRefreshToken.is_revoked == False,
        )
    )
    matched_token = result.scalar_one_or_none()

    if not matched_token:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_grant"},
        )

    # Check expiry
    expires_at = matched_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_grant"},
        )

    scopes = set(matched_token.scope.split()) if matched_token.scope else {"openid"}

    id_token = create_id_token(
        email=matched_token.email,
        client_id=client_id,
        nonce=None,
        scopes=scopes,
        settings=settings,
    )
    access_token = create_oidc_access_token(
        email=matched_token.email,
        client_id=client_id,
        scopes=scopes,
        settings=settings,
    )

    return JSONResponse(
        content={
            "access_token": access_token,
            "id_token": id_token,
            "token_type": "Bearer",
            "expires_in": settings.OIDC_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "scope": matched_token.scope or "openid",
        }
    )


async def _handle_client_credentials(
    db: AsyncSession,
    settings,
    client_id: str | None,
    client_secret: str | None,
    scope: str | None,
):
    if not client_id or not client_secret:
        return JSONResponse(
            status_code=401,
            content={"error": "invalid_client"},
        )

    app = await verify_client_credentials(db, client_id, client_secret)
    if not app:
        return JSONResponse(
            status_code=401,
            content={"error": "invalid_client"},
        )

    # client_credentials only for machine_to_machine apps
    if app.application_type != "machine_to_machine":
        return JSONResponse(
            status_code=400,
            content={"error": "unauthorized_client"},
        )

    requested_scopes = set(scope.split()) if scope else {"openid"}

    access_token = create_oidc_access_token(
        user_id=client_id,
        client_id=client_id,
        scopes=requested_scopes,
        settings=settings,
    )

    return JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": settings.OIDC_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "scope": " ".join(sorted(requested_scopes)),
        }
    )
