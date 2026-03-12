from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.services.oidc.token_service import validate_access_token

router = APIRouter()


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization[7:]


async def _handle_userinfo(
    authorization: str | None,
    db: AsyncSession,
):
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

    result = await db.execute(select(User).where(User.id == sub))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scope_str = payload.get("scope", "openid")
    scopes = set(scope_str.split())

    claims: dict = {"sub": user.id}
    if "profile" in scopes:
        claims["name"] = user.full_name
    if "email" in scopes:
        claims["email"] = user.email
        claims["email_verified"] = user.is_verified

    return JSONResponse(content=claims)


@router.get("/userinfo")
async def userinfo_get(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await _handle_userinfo(authorization, db)


@router.post("/userinfo")
async def userinfo_post(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await _handle_userinfo(authorization, db)
