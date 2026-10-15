from datetime import date, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Booking


class BookingRepository:
    """Persistence operations for interview booking requests."""

    def create(
        self,
        db: Session,
        name: str,
        email: str,
        interview_date: date,
        interview_time: time,
    ) -> Booking:
        """Create and persist an interview booking request."""
        booking = Booking(
            name=name.strip(),
            email=email.strip().lower(),
            interview_date=interview_date,
            interview_time=interview_time,
            status="requested",
        )

        try:
            db.add(booking)
            db.commit()
            db.refresh(booking)
            return booking
        except Exception:
            db.rollback()
            raise

    def get_by_id(self, db: Session, booking_id: int) -> Booking | None:
        """Find a booking by its primary key."""
        return db.get(Booking, booking_id)

    def list_by_email(self, db: Session, email: str) -> list[Booking]:
        """List bookings associated with an email address."""
        statement = (
            select(Booking)
            .where(Booking.email == email.strip().lower())
            .order_by(Booking.created_at.desc())
        )
        return list(db.scalars(statement).all())

    def update_status(
        self,
        db: Session,
        booking_id: int,
        status: str,
    ) -> Booking | None:
        """Update the status of a booking request."""
        booking = db.get(Booking, booking_id)
        if booking is None:
            return None

        booking.status = status

        try:
            db.commit()
            db.refresh(booking)
            return booking
        except Exception:
            db.rollback()
            raise


booking_repository = BookingRepository()
