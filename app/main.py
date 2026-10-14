
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.core.config import get_settings
from app.db.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize application resources on startup."""
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Document ingestion, conversational RAG, "
        "and interview booking APIs."
    ),
    lifespan=lifespan,
)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    """Return basic API information."""
    return {
        "message": "Palm Mind RAG API is running",
        "version": settings.app_version,
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Check whether the API process is responding."""
    return {"status": "ok"}
