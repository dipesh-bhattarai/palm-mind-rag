from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Document


class DocumentRepository:
    """Persistence operations for document metadata."""

    def create(self, db: Session, document: Document) -> Document:
        """Save a document record and return the persisted instance."""
        try:
            db.add(document)
            db.commit()
            db.refresh(document)
            return document
        except Exception:
            db.rollback()
            raise

    def get_by_id(self, db: Session, document_id: str) -> Document | None:
        """Find a document by its ID."""
        return db.get(Document, document_id)

    def list_all(self, db: Session) -> list[Document]:
        """Return document records ordered newest first."""
        statement = select(Document).order_by(Document.created_at.desc())
        return list(db.scalars(statement).all())

    def update_status(
        self,
        db: Session,
        document_id: str,
        status: str,
        error_message: str | None = None,
    ) -> Document | None:
        """Update processing status and optional error details."""
        document = db.get(Document, document_id)
        if document is None:
            return None

        document.status = status
        document.error_message = error_message

        try:
            db.commit()
            db.refresh(document)
            return document
        except Exception:
            db.rollback()
            raise

    def delete(self, db: Session, document_id: str) -> bool:
        """Delete a document metadata record."""
        document = db.get(Document, document_id)
        if document is None:
            return False

        try:
            db.delete(document)
            db.commit()
            return True
        except Exception:
            db.rollback()
            raise


document_repository = DocumentRepository()
