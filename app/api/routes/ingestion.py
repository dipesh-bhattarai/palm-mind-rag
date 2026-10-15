
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Document
from app.repositories.vector_repository import vector_repository
from app.schemas.documents import (
    ChunkingStrategy,
    DocumentUploadResponse,
)
from app.services.embedding_service import embedding_service
from app.services.ingestion_service import process_document
from app.repositories.document_repository import document_repository

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=201,
)
def upload_document(
    file: UploadFile = File(...),
    chunking_strategy: ChunkingStrategy = Form("recursive"),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    """Upload a PDF/TXT file, create embeddings, and store chunks."""

    filename = file.filename or "document"

    if not filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(
            status_code=415,
            detail="Only PDF and TXT files are supported.",
        )

    file_type = filename.rsplit(".", 1)[-1].lower()
    document_id = str(uuid4())

    try:
        file_bytes = file.file.read(MAX_FILE_SIZE + 1)

        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File size must not exceed 10 MB.",
            )

        chunks = process_document(
            file_bytes=file_bytes,
            file_type=file_type,
            strategy=chunking_strategy,
        )

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="No text chunks could be extracted from this file.",
            )

        embeddings = embedding_service.embed_documents(chunks)

        vector_repository.store_chunks(
            document_id=document_id,
            filename=filename,
            chunks=chunks,
            embeddings=embeddings,
        )

    except HTTPException:
        raise
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Document processing or vector storage failed. "
                "Check that the embedding model and Qdrant are available."
            ),
        ) from exc
    finally:
        file.file.close()

        document = Document(
        id=document_id,
        filename=filename,
        file_type=file_type,
        chunking_strategy=chunking_strategy,
        status="completed",
    )

    try:
        document_repository.create(db, document)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to save document metadata.",
        ) from exc

    return DocumentUploadResponse(
        document_id=document_id,
        filename=filename,
        file_type=file_type,
        chunking_strategy=chunking_strategy,
        chunk_count=len(chunks),
        status=document.status,
    )
