from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.scan import ScanResponse, ScanCreate

router = APIRouter()


@router.get("/", response_model=list[ScanResponse])
async def list_scans(db: AsyncSession = Depends(get_db)):
    """List all scan history."""
    # TODO: Implement
    return []


@router.post("/", response_model=ScanResponse)
async def trigger_scan(
    scan: ScanCreate,
    db: AsyncSession = Depends(get_db),
):
    """Trigger a new scan for exposures."""
    # TODO: Implement - queue Celery task
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: int, db: AsyncSession = Depends(get_db)):
    """Get details and results of a specific scan."""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not implemented")
