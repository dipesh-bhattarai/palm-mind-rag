
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Document
from app.schemas.documents import (
    ChunkingStrategy,
    DocumentUploadResponse,
)
from app.services.ingestion_service import process_document

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
    """Upload a PDF/TXT file and process its text."""
    filename = file.filename or "document"

    if not filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(
            status_code=415,
            detail="Only PDF and TXT files are supported.",
        )

    file_type = filename.rsplit(".", 1)[-1].lower()

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

    except HTTPException:
        raise
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail="Unable to extract text from this file.",
        ) from exc
    finally:
        file.file.close()

    document_id = str(uuid4())

    document = Document(
        id=document_id,
        filename=filename,
        file_type=file_type,
        chunking_strategy=chunking_strategy,
        status="text_extracted",
    )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except SQLAlchemyError as exc:
        db.rollback()
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
