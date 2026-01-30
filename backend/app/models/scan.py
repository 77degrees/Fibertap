from datetime import datetime
from sqlalchemy import String, DateTime, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class ScanStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanType(enum.Enum):
    FULL = "full"  # All sources
    BREACH = "breach"  # HIBP only
    DATA_BROKER = "data_broker"  # Data brokers only


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(primary_key=True)
    scan_type: Mapped[ScanType] = mapped_column(Enum(ScanType))
    status: Mapped[ScanStatus] = mapped_column(Enum(ScanStatus), default=ScanStatus.PENDING)

    exposures_found: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
