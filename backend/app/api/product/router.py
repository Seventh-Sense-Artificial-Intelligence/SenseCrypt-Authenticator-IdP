from fastapi import APIRouter
from app.api.product.applications import router as applications_router

# ── Product Routes ──
# Import and include product-specific routers here.

router = APIRouter(prefix="/product", tags=["product"])
router.include_router(applications_router)
