from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum


from app.core.database import Base


class ExposureStatus(enum.Enum):
    DETECTED = "detected"
    REMOVAL_REQUESTED = "removal_requested"
    REMOVAL_IN_PROGRESS = "removal_in_progress"
    REMOVED = "removed"
    REMOVAL_FAILED = "removal_failed"


class ExposureSource(enum.Enum):
    DATA_BROKER = "data_broker"
    BREACH = "breach"
    PEOPLE_SEARCH = "people_search"
    OTHER = "other"


class Exposure(Base):
    __tablename__ = "exposures"

    id: Mapped[int] = mapped_column(primary_key=True)
    family_member_id: Mapped[int] = mapped_column(ForeignKey("family_members.id"))

    source: Mapped[ExposureSource] = mapped_column(Enum(ExposureSource))
    source_name: Mapped[str] = mapped_column(String(255))  # e.g., "Spokeo", "LinkedIn breach"
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    data_exposed: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON of exposed fields
    status: Mapped[ExposureStatus] = mapped_column(
        Enum(ExposureStatus), default=ExposureStatus.DETECTED
    )

    incogni_request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    family_member: Mapped["FamilyMember"] = relationship(back_populates="exposures")
