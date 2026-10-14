
from functools import lru_cache

from langchain_groq import ChatGroq
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from app.core.config import settings
from app.services.memory_service import conversation_memory
from app.services.retrieval_service import retrieve_chunks


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    """Create and reuse the Groq chat model."""
    if not settings.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Configure it in your .env file."
        )

    return ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=settings.groq_api_key,
        temperature=0,
    )


def answer_question(
    question: str,
    session_id: str,
    document_id: str | None = None,
) -> dict:
    """Answer a question using retrieved context and conversation history."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not session_id.strip():
        raise ValueError("Session ID cannot be empty.")

    history = conversation_memory.get_history(session_id)

    # Retrieve using the current question.
    chunks = retrieve_chunks(
        question=question,
        limit=5,
        document_id=document_id,
    )

    if not chunks:
        answer = (
            "I couldn't find relevant information in the uploaded "
            "documents to answer that question."
        )
        conversation_memory.add_message(session_id, "user", question)
        conversation_memory.add_message(session_id, "assistant", answer)
        return {"answer": answer, "sources": []}

    context_parts = []
    sources = []

    for index, chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"[Source {index}]\n"
            f"Filename: {chunk['filename']}\n"
            f"Chunk index: {chunk['chunk_index']}\n"
            f"Content:\n{chunk['text']}"
        )

        sources.append(
            {
                "filename": chunk["filename"],
                "chunk_index": chunk["chunk_index"],
                "score": chunk["score"],
                "text": chunk["text"],
            }
        )

    context = "\n\n".join(context_parts)

    messages = [
        SystemMessage(
            content=(
                "You are a document question-answering assistant. "
                "Use the conversation history to understand follow-up "
                "questions, but answer factual questions about documents "
                "using only the retrieved document context. "
                "If the context is insufficient, say so clearly. "
                "Do not invent facts. Cite supporting passages using "
                "[Source 1], [Source 2], and so on."
            )
        )
    ]

    # Include previous user/assistant turns.
    for item in history[-10:]:
        if item["role"] == "user":
            messages.append(HumanMessage(content=item["content"]))
        elif item["role"] == "assistant":
            messages.append(AIMessage(content=item["content"]))

    messages.append(
        HumanMessage(
            content=(
                f"Current question:\n{question}\n\n"
                f"Retrieved document context:\n{context}"
            )
        )
    )

    response = get_llm().invoke(messages)
    answer = str(response.content)

    conversation_memory.add_message(session_id, "user", question)
    conversation_memory.add_message(session_id, "assistant", answer)

    return {
        "answer": answer,
        "sources": sources,
    }
