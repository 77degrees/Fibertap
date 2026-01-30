from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.exposure import ExposureResponse

router = APIRouter()


@router.get("/", response_model=list[ExposureResponse])
async def list_exposures(
    member_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all detected data exposures, optionally filtered by family member."""
    # TODO: Implement
    return []


@router.get("/{exposure_id}", response_model=ExposureResponse)
async def get_exposure(exposure_id: int, db: AsyncSession = Depends(get_db)):
    """Get details for a specific exposure."""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/{exposure_id}/request-removal")
async def request_removal(exposure_id: int, db: AsyncSession = Depends(get_db)):
    """Submit a removal request for this exposure via Incogni."""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not implemented")
