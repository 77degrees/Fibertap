from fastapi import APIRouter

from app.api.routes import health, family_members, exposures, scans
from app.api import auth

router = APIRouter()

router.include_router(health.router, tags=["health"])
router.include_router(family_members.router, prefix="/family-members", tags=["family-members"])
router.include_router(exposures.router, prefix="/exposures", tags=["exposures"])
router.include_router(scans.router, prefix="/scans", tags=["scans"])
router.include_router(auth.router)
