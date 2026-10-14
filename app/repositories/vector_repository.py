
from uuid import uuid4

from qdrant_client import QdrantClient, models

from app.core.config import settings


COLLECTION_NAME = "documents"
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


vector_repository = VectorRepository()
