import re
from datetime import date, time

from sqlalchemy.orm import Session

from app.services.booking_intent_service import extract_booking_intent
from app.services.booking_service import create_booking
from app.services.memory_service import conversation_memory


def normalize_message(message: str) -> str:
    """Normalize a short response for reliable yes/no matching."""
    message = message.lower().replace("’", "'").strip()
    message = re.sub(r"[^a-z0-9\s']", "", message)
    return " ".join(message.split())


def handle_booking_message(
    question: str,
    session_id: str,
    history: list[dict[str, str]],
    db: Session,
) -> dict | None:
    """Handle interview booking messages; return None if unrelated."""

    draft = conversation_memory.get_booking_draft(session_id) or {}
    intent = extract_booking_intent(question, history)

    if not intent.booking_requested and not draft:
        return None

    normalized_question = normalize_message(question)

    # Allow the user to cancel at any point in the booking flow.
    cancellation_phrases = {
        "cancel",
        "cancel it",
        "cancel booking",
        "cancel the booking",
        "stop booking",
        "never mind",
        "nevermind",
        "forget it",
        "no",
        "nope",
        "no thanks",
        "no thank you",
        "no i dont want to book it",
        "i dont want to book it",
        "i do not want to book it",
        "i dont want to book",
        "i do not want to book",
    }

    if draft and normalized_question in cancellation_phrases:
        conversation_memory.clear_booking_draft(session_id)
        return {
            "answer": (
                "No booking has been created. "
                "I've cancelled the interview booking request."
            ),
            "booking": None,
            "status": "cancelled",
        }

    # Merge any newly extracted details into the existing draft.
    # If details change after confirmation was requested, ask for
    # confirmation again using the updated information.
    details_changed = False

    for field in ("name", "email", "interview_date", "interview_time"):
        value = getattr(intent, field)

        if value and draft.get(field) != value:
            draft[field] = value
            details_changed = True

    if details_changed:
        draft.pop("confirmation_requested", None)

    # Collect all required fields before asking for confirmation.
    required_fields = (
        "name",
        "email",
        "interview_date",
        "interview_time",
    )
    missing = [field for field in required_fields if not draft.get(field)]

    if missing:
        conversation_memory.save_booking_draft(session_id, draft)

        prompts = {
            "name": "your full name",
            "email": "your email address",
            "interview_date": "your preferred interview date (YYYY-MM-DD)",
            "interview_time": (
                "your preferred interview time (HH:MM, 24-hour format)"
            ),
        }

        next_field = missing[0]

        return {
            "answer": (
                "Sure, I can help arrange an interview. "
                f"Could you provide {prompts[next_field]}?"
            ),
            "booking": None,
            "status": "collecting_details",
        }

    # Validate date and time formats.
    try:
        interview_date = date.fromisoformat(draft["interview_date"])
        interview_time = time.fromisoformat(draft["interview_time"])
    except (TypeError, ValueError):
        conversation_memory.save_booking_draft(session_id, draft)
        return {
            "answer": (
                "I couldn't interpret the date or time. "
                "Please provide the date as YYYY-MM-DD and time as HH:MM."
            ),
            "booking": None,
            "status": "invalid_details",
        }

    # Reject past dates.
    if interview_date < date.today():
        draft.pop("interview_date", None)
        draft.pop("confirmation_requested", None)
        conversation_memory.save_booking_draft(session_id, draft)

        return {
            "answer": "That date is in the past. What future date would you prefer?",
            "booking": None,
            "status": "invalid_details",
        }

    # Present the collected details and wait for the user's confirmation.
    if not draft.get("confirmation_requested"):
        draft["confirmation_requested"] = True
        conversation_memory.save_booking_draft(session_id, draft)

        return {
            "answer": (
                "Please confirm your interview request:\n"
                f"Name: {draft['name']}\n"
                f"Email: {draft['email']}\n"
                f"Date: {interview_date.isoformat()}\n"
                f"Time: {interview_time.strftime('%H:%M')}\n\n"
                "Would you like me to submit this booking request? "
                "Please reply yes or no."
            ),
            "booking": None,
            "status": "awaiting_confirmation",
        }

    # Only clear, explicit affirmative responses can submit a booking.
    affirmative_answers = {
        "yes",
        "yes please",
        "yes confirm",
        "yes i confirm",
        "yes i confirm the booking",
        "i confirm",
        "i confirm the booking",
        "confirm",
        "confirm booking",
        "confirm the booking",
        "go ahead",
        "go ahead please",
        "that is correct",
        "thats correct",
        "looks good confirm",
    }

    if normalized_question not in affirmative_answers:
        return {
            "answer": (
                "I haven't submitted the booking yet. "
                "Please reply yes to confirm, or no to cancel."
            ),
            "booking": None,
            "status": "awaiting_confirmation",
        }

    # Save only after explicit confirmation.
    try:
        booking = create_booking(
            db=db,
            name=draft["name"],
            email=draft["email"],
            interview_date=interview_date,
            interview_time=interview_time,
        )
    except ValueError as exc:
        return {
            "answer": str(exc),
            "booking": None,
            "status": "invalid_details",
        }

    conversation_memory.clear_booking_draft(session_id)

    return {
        "answer": (
            "Your interview request has been recorded for "
            f"{booking.interview_date.isoformat()} at "
            f"{booking.interview_time.strftime('%H:%M')}. "
            f"Your booking reference is {booking.id}."
        ),
        "booking": {
            "id": booking.id,
            "name": booking.name,
            "email": booking.email,
            "interview_date": booking.interview_date.isoformat(),
            "interview_time": booking.interview_time.strftime("%H:%M"),
            "status": booking.status,
        },
        "status": "requested",
    }
