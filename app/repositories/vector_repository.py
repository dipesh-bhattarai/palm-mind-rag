
from uuid import uuid4
from typing import Any

from qdrant_client import QdrantClient, models

from app.core.config import settings


COLLECTION_NAME = settings.qdrant_collection
VECTOR_SIZE = 384


class VectorRepository:
    def __init__(self):
        self.client = QdrantClient(url=settings.qdrant_url)
        self.ensure_collection()

    def ensure_collection(self) -> None:
        if not self.client.collection_exists(COLLECTION_NAME):
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=models.Distance.COSINE,
                ),
            )

    def store_chunks(
        self,
        document_id: str,
        filename: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> None:
        points = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            points.append(
                models.PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload={
                        "document_id": document_id,
                        "filename": filename,
                        "chunk_index": index,
                        "text": chunk,
                    },
                )
            )

        if points:
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
            )

    def search(
        self,
        query_embedding: list[float],
        limit: int = 5,
        document_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return the most similar chunks for a query embedding."""

        query_filter = None

        if document_id:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id),
                    )
                ]
            )

        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        ).points

        return [
            {
                "document_id": point.payload.get("document_id"),
                "filename": point.payload.get("filename"),
                "chunk_index": point.payload.get("chunk_index"),
                "text": point.payload.get("text"),
                "score": point.score,
            }
            for point in results
            if point.payload is not None
        ]


vector_repository = VectorRepository()
