
from typing import Literal

from pydantic import BaseModel, ConfigDict


ChunkingStrategy = Literal["fixed_size", "recursive"]


class DocumentUploadResponse(BaseModel):
    """Response returned after document text is processed."""

    model_config = ConfigDict(from_attributes=True)

    document_id: str
    filename: str
    file_type: Literal["pdf", "txt"]
    chunking_strategy: ChunkingStrategy
    chunk_count: int
    status: str
