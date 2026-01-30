from datetime import datetime
from pydantic import BaseModel

from app.models.exposure import ExposureStatus, ExposureSource


class ExposureResponse(BaseModel):
    id: int
    family_member_id: int
    source: ExposureSource
    source_name: str
    source_url: str | None
    data_exposed: str | None
    status: ExposureStatus
    incogni_request_id: str | None
    detected_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
