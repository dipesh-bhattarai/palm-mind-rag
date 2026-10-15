from datetime import date, time
from types import SimpleNamespace
from unittest.mock import Mock

from app.services import booking_conversation_service as booking_service


def test_booking_cancellation_clears_pending_draft(monkeypatch):
    session_id = "test-cancel-session"

    monkeypatch.setattr(
        booking_service.conversation_memory,
        "get_booking_draft",
        lambda _: {
            "name": "Test Candidate",
            "email": "test@example.com",
            "interview_date": "2026-10-28",
            "interview_time": "15:00",
            "confirmation_requested": True,
        },
    )

    clear_draft = Mock()
    monkeypatch.setattr(
        booking_service.conversation_memory,
        "clear_booking_draft",
        clear_draft,
    )

    monkeypatch.setattr(
        booking_service,
        "extract_booking_intent",
        lambda *_: SimpleNamespace(
            booking_requested=True,
            confirmed=False,
            name=None,
            email=None,
            interview_date=None,
            interview_time=None,
        ),
    )

    create_booking = Mock()
    monkeypatch.setattr(
        booking_service,
        "create_booking",
        create_booking,
    )

    result = booking_service.handle_booking_message(
        question="No",
        session_id=session_id,
        history=[],
        db=Mock(),
    )

    assert result["status"] == "cancelled"
    assert result["booking"] is None
    clear_draft.assert_called_once_with(session_id)
    create_booking.assert_not_called()


def test_explicit_yes_creates_booking(monkeypatch):
    session_id = "test-confirm-session"

    draft = {
        "name": "Test Candidate",
        "email": "test@example.com",
        "interview_date": "2026-10-28",
        "interview_time": "15:00",
        "confirmation_requested": True,
    }

    monkeypatch.setattr(
        booking_service.conversation_memory,
        "get_booking_draft",
        lambda _: draft.copy(),
    )

    clear_draft = Mock()
    monkeypatch.setattr(
        booking_service.conversation_memory,
        "clear_booking_draft",
        clear_draft,
    )

    monkeypatch.setattr(
        booking_service,
        "extract_booking_intent",
        lambda *_: SimpleNamespace(
            booking_requested=True,
            confirmed=False,
            name=None,
            email=None,
            interview_date=None,
            interview_time=None,
        ),
    )

    saved_booking = SimpleNamespace(
        id=123,
        name="Test Candidate",
        email="test@example.com",
        interview_date=date(2026, 10, 28),
        interview_time=time(15, 0),
        status="requested",
    )

    create_booking = Mock(return_value=saved_booking)
    monkeypatch.setattr(
        booking_service,
        "create_booking",
        create_booking,
    )

    result = booking_service.handle_booking_message(
        question="Yes",
        session_id=session_id,
        history=[],
        db=Mock(),
    )

    assert result["status"] == "requested"
    assert result["booking"]["id"] == 123
    create_booking.assert_called_once()
    clear_draft.assert_called_once_with(session_id)


def test_unconfirmed_booking_is_not_saved(monkeypatch):
    session_id = "test-wait-session"

    monkeypatch.setattr(
        booking_service.conversation_memory,
        "get_booking_draft",
        lambda _: {
            "name": "Test Candidate",
            "email": "test@example.com",
            "interview_date": "2026-10-28",
            "interview_time": "15:00",
            "confirmation_requested": True,
        },
    )

    monkeypatch.setattr(
        booking_service,
        "extract_booking_intent",
        lambda *_: SimpleNamespace(
            booking_requested=True,
            confirmed=False,
            name=None,
            email=None,
            interview_date=None,
            interview_time=None,
        ),
    )

    create_booking = Mock()
    monkeypatch.setattr(
        booking_service,
        "create_booking",
        create_booking,
    )

    result = booking_service.handle_booking_message(
        question="I'm not sure yet",
        session_id=session_id,
        history=[],
        db=Mock(),
    )

    assert result["status"] == "awaiting_confirmation"
    assert result["booking"] is None
    create_booking.assert_not_called()
