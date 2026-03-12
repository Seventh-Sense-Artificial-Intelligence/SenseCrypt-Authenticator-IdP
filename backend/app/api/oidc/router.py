from fastapi import APIRouter
from app.api.oidc.discovery import router as discovery_router
from app.api.oidc.authorize import router as authorize_router
from app.api.oidc.token import router as token_router
from app.api.oidc.userinfo import router as userinfo_router
from app.api.oidc.challenge import router as challenge_router

oidc_router = APIRouter(tags=["oidc"])
oidc_router.include_router(discovery_router)
oidc_router.include_router(authorize_router)
oidc_router.include_router(token_router)
oidc_router.include_router(userinfo_router)
oidc_router.include_router(challenge_router)
