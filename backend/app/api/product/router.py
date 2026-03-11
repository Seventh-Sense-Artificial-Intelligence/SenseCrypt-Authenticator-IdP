from fastapi import APIRouter

# ── Product Routes ──
# Import and include product-specific routers here.
#
# Example:
#   from app.api.product.analytics import router as analytics_router
#   router.include_router(analytics_router)

router = APIRouter(prefix="/product", tags=["product"])
