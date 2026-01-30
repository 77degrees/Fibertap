from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.scan import Scan, ScanStatus, ScanType
from app.schemas.scan import ScanResponse, ScanCreate
from app.tasks.scanning import run_breach_scan, run_data_broker_scan, run_full_scan

router = APIRouter()


@router.get("/", response_model=list[ScanResponse])
async def list_scans(db: AsyncSession = Depends(get_db)):
    """List all scan history."""
    result = await db.execute(select(Scan).order_by(Scan.started_at.desc()))
    return result.scalars().all()


@router.post("/", response_model=ScanResponse, status_code=201)
async def trigger_scan(
    scan: ScanCreate,
    db: AsyncSession = Depends(get_db),
):
    """Trigger a new scan for exposures."""
    # Create scan record
    db_scan = Scan(
        scan_type=scan.scan_type,
        status=ScanStatus.PENDING,
    )
    db.add(db_scan)
    await db.commit()
    await db.refresh(db_scan)

    # Queue the appropriate Celery task
    if scan.scan_type == ScanType.BREACH:
        run_breach_scan.delay(scan.family_member_ids, db_scan.id)
    elif scan.scan_type == ScanType.DATA_BROKER:
        run_data_broker_scan.delay(scan.family_member_ids, db_scan.id)
    elif scan.scan_type == ScanType.FULL:
        run_breach_scan.delay(scan.family_member_ids, db_scan.id)
        run_data_broker_scan.delay(scan.family_member_ids, db_scan.id)

    return db_scan


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: int, db: AsyncSession = Depends(get_db)):
    """Get details and results of a specific scan."""
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan
