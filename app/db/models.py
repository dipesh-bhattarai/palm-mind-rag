
from datetime import date, datetime, time, timezone

from sqlalchemy import Date, DateTime, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Document(Base):
    """Metadata for an uploaded document."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True
    )
    filename: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    file_type: Mapped[str] = mapped_column(
        String(10), nullable=False
    )
    chunking_strategy: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), default="pending", nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Booking(Base):
    """An interview booking request."""

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(254), nullable=False, index=True
    )
    interview_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    interview_time: Mapped[time] = mapped_column(
        Time, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), default="requested", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
