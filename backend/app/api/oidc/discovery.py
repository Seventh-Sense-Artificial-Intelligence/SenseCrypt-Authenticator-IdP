from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.services.oidc.keys import get_jwks_document

router = APIRouter()


@router.get("/.well-known/openid-configuration")
async def openid_configuration():
    settings = get_settings()
    issuer = settings.OIDC_ISSUER_URL

    return JSONResponse(
        content={
            "issuer": issuer,
            "authorization_endpoint": f"{issuer}/authorize",
            "token_endpoint": f"{issuer}/token",
            "userinfo_endpoint": f"{issuer}/userinfo",
            "jwks_uri": f"{issuer}/jwks",
            "scopes_supported": ["openid", "profile", "email", "offline_access"],
            "response_types_supported": ["code"],
            "grant_types_supported": [
                "authorization_code",
                "refresh_token",
                "client_credentials",
            ],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
            "token_endpoint_auth_methods_supported": [
                "client_secret_basic",
                "client_secret_post",
            ],
            "claims_supported": [
                "sub",
                "iss",
                "aud",
                "exp",
                "iat",
                "nonce",
                "email",
                "email_verified",
                "name",
            ],
        }
    )


@router.get("/jwks")
async def jwks():
    return JSONResponse(content=get_jwks_document())
