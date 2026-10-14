
from app.repositories.vector_repository import vector_repository
from app.services.embedding_service import embedding_service


def retrieve_chunks(
    question: str,
    limit: int = 5,
    document_id: str | None = None,
) -> list[dict]:
    """Embed a question and retrieve relevant document chunks."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    query_embedding = embedding_service.embed_query(question)

    return vector_repository.search(
        query_embedding=query_embedding,
        limit=limit,
        document_id=document_id,
    )
