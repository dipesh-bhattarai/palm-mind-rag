from app.core.config import settings


class EmbeddingService:
    """Load the embedding model only when embeddings are needed."""

    def __init__(self):
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                settings.embedding_model,
                device="cpu",
            )

        return self._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._get_model().encode(
            texts,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self._get_model().encode(
            text,
            normalize_embeddings=True,
        )
        return embedding.tolist()


embedding_service = EmbeddingService()
