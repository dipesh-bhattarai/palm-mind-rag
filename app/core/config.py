
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Palm Mind RAG API"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = "sqlite:///./palm_mind.db"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "documents"
    redis_url: str = "redis://localhost:6379/0"

    groq_api_key: str = ""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
