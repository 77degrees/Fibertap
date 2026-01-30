from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.exposure import Exposure, ExposureStatus
from app.schemas.exposure import ExposureResponse, ExposureUpdate

router = APIRouter()


@router.get("/", response_model=list[ExposureResponse])
async def list_exposures(
    member_id: int | None = None,
    status: ExposureStatus | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all detected data exposures, optionally filtered by family member or status."""
    query = select(Exposure).order_by(Exposure.detected_at.desc())

    if member_id is not None:
        query = query.where(Exposure.family_member_id == member_id)
    if status is not None:
        query = query.where(Exposure.status == status)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{exposure_id}", response_model=ExposureResponse)
async def get_exposure(exposure_id: int, db: AsyncSession = Depends(get_db)):
    """Get details for a specific exposure."""
    result = await db.execute(select(Exposure).where(Exposure.id == exposure_id))
    exposure = result.scalar_one_or_none()
    if not exposure:
        raise HTTPException(status_code=404, detail="Exposure not found")
    return exposure


@router.put("/{exposure_id}", response_model=ExposureResponse)
async def update_exposure(
    exposure_id: int,
    exposure_update: ExposureUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an exposure's status or details."""
    result = await db.execute(select(Exposure).where(Exposure.id == exposure_id))
    exposure = result.scalar_one_or_none()
    if not exposure:
        raise HTTPException(status_code=404, detail="Exposure not found")

    update_data = exposure_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exposure, field, value)

    await db.commit()
    await db.refresh(exposure)
    return exposure


@router.post("/{exposure_id}/request-removal", response_model=ExposureResponse)
async def request_removal(exposure_id: int, db: AsyncSession = Depends(get_db)):
    """Mark exposure as removal requested (for manual tracking)."""
    result = await db.execute(select(Exposure).where(Exposure.id == exposure_id))
    exposure = result.scalar_one_or_none()
    if not exposure:
        raise HTTPException(status_code=404, detail="Exposure not found")

    exposure.status = ExposureStatus.REMOVAL_REQUESTED
    await db.commit()
    await db.refresh(exposure)
    return exposure


@router.post("/{exposure_id}/mark-removed", response_model=ExposureResponse)
async def mark_removed(exposure_id: int, db: AsyncSession = Depends(get_db)):
    """Mark exposure as removed."""
    result = await db.execute(select(Exposure).where(Exposure.id == exposure_id))
    exposure = result.scalar_one_or_none()
    if not exposure:
        raise HTTPException(status_code=404, detail="Exposure not found")

    exposure.status = ExposureStatus.REMOVED
    await db.commit()
    await db.refresh(exposure)
    return exposure


@router.delete("/{exposure_id}", status_code=204)
async def delete_exposure(exposure_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an exposure (e.g., if it was a false positive)."""
    result = await db.execute(select(Exposure).where(Exposure.id == exposure_id))
    exposure = result.scalar_one_or_none()
    if not exposure:
        raise HTTPException(status_code=404, detail="Exposure not found")

    await db.delete(exposure)
    await db.commit()
