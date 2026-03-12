from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from app.services.oidc.token_service import validate_access_token

router = APIRouter()


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization[7:]


async def _handle_userinfo(authorization: str | None):
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = validate_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=401,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scope_str = payload.get("scope", "openid")
    scopes = set(scope_str.split())

    claims: dict = {"sub": sub}
    if "profile" in scopes:
        claims["name"] = sub
    if "email" in scopes:
        claims["email"] = sub
        claims["email_verified"] = True

    return JSONResponse(content=claims)


@router.get("/userinfo")
async def userinfo_get(authorization: str | None = Header(default=None)):
    return await _handle_userinfo(authorization)


@router.post("/userinfo")
async def userinfo_post(authorization: str | None = Header(default=None)):
    return await _handle_userinfo(authorization)
