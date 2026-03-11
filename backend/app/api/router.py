from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.users import router as users_router

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(users_router)
