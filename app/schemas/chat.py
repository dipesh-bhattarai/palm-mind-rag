
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for conversational RAG and interview booking."""

    question: str = Field(min_length=1, max_length=10_000)
    session_id: str = Field(min_length=1, max_length=200)
    document_id: str | None = None
