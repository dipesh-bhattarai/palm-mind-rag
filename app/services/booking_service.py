from datetime import date, time

from sqlalchemy.orm import Session

from app.db.models import Booking
from app.repositories.booking_repository import booking_repository


def create_booking(
    db: Session,
    name: str,
    email: str,
    interview_date: date,
    interview_time: time,
) -> Booking:
    """Validate and save an interview booking."""

    name = name.strip()
    email = email.strip().lower()

    if not name:
        raise ValueError("Name is required.")

    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        raise ValueError("Please provide a valid email address.")

    if interview_date < date.today():
        raise ValueError("Interview date cannot be in the past.")

    return booking_repository.create(
        db=db,
        name=name,
        email=email,
        interview_date=interview_date,
        interview_time=interview_time,
    )