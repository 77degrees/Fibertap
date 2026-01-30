from datetime import datetime
from pydantic import BaseModel

from app.models.scan import ScanStatus, ScanType


class ScanCreate(BaseModel):
    scan_type: ScanType = ScanType.FULL
    family_member_ids: list[int] | None = None  # None = scan all


class ScanResponse(BaseModel):
    id: int
    scan_type: ScanType
    status: ScanStatus
    exposures_found: int
    error_message: str | None
    started_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True
