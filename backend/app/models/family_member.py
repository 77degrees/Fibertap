from datetime import datetime
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FamilyMember(Base):
    __tablename__ = "family_members"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Name fields
    first_name: Mapped[str] = mapped_column(String(100))
    middle_initial: Mapped[str | None] = mapped_column(String(5), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100))

    # Legacy field for backwards compatibility (computed from first + last)
    name: Mapped[str] = mapped_column(String(255))

    # Contact info - arrays stored as JSON (up to 5 each)
    emails: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    phone_numbers: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    addresses: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    # Legacy single fields (deprecated, kept for migration)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    date_of_birth: Mapped[str | None] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    exposures: Mapped[list["Exposure"]] = relationship(back_populates="family_member")

    @property
    def full_name(self) -> str:
        """Get full name with middle initial if present."""
        if self.middle_initial:
            return f"{self.first_name} {self.middle_initial}. {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @property
    def primary_email(self) -> str | None:
        """Get first email from list."""
        if self.emails and len(self.emails) > 0:
            return self.emails[0]
        return self.email  # Fallback to legacy field
