
from pydantic import BaseModel, Field


class BookingIntent(BaseModel):
    """Structured booking details extracted from conversation."""

    booking_requested: bool = Field(
        description="Whether the candidate wants to book an interview."
    )
    name: str | None = Field(
        default=None,
        description="Candidate's full name, if provided."
    )
    email: str | None = Field(
        default=None,
        description="Candidate's email address, if provided."
    )
    interview_date: str | None = Field(
        default=None,
        description="Requested interview date in YYYY-MM-DD format."
    )
    interview_time: str | None = Field(
        default=None,
        description="Requested interview time in 24-hour HH:MM format."
    )
    confirmed: bool = Field(
        default=False,
        description=(
            "Whether the candidate explicitly confirms the booking "
            "after being shown the collected details."
        )
    )
