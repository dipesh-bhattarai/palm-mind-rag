import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.chat import ChatRequest
from app.services.booking_conversation_service import handle_booking_message
from app.services.memory_service import conversation_memory
from app.services.rag_service import answer_question

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


@router.post("")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Handle document questions and interview booking conversations."""

    question = request.question.strip()
    session_id = request.session_id.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    if not session_id:
        raise HTTPException(
            status_code=422,
            detail="Session ID cannot be empty.",
        )

    try:
        history = conversation_memory.get_history(session_id)

        booking_result = handle_booking_message(
            question=question,
            session_id=session_id,
            history=history,
            db=db,
        )

        if booking_result is not None:
            conversation_memory.add_message(session_id, "user", question)
            conversation_memory.add_message(
                session_id,
                "assistant",
                booking_result["answer"],
            )
            return {
                **booking_result,
                "sources": [],
            }

        rag_result = answer_question(
            question=question,
            session_id=session_id,
            document_id=request.document_id,
        )

        return {
            **rag_result,
            "status": "answered",
            "booking": None,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=500,
            detail="The chat request could not be processed.",
        ) from exc
