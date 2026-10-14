
import fitz

from app.schemas.documents import ChunkingStrategy
from app.services.chunking_service import chunk_text


def extract_text(file_bytes: bytes, file_type: str) -> str:
    """Extract text from PDF or UTF-8 TXT bytes."""
    if file_type == "pdf":
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            text = "\n\n".join(page.get_text() for page in pdf)

    elif file_type == "txt":
        text = file_bytes.decode("utf-8-sig")

    else:
        raise ValueError("Unsupported file type.")

    text = text.strip()

    if not text:
        raise ValueError(
            "No extractable text found in the document."
        )

    return text


def process_document(
    file_bytes: bytes,
    file_type: str,
    strategy: ChunkingStrategy,
) -> list[str]:
    """Extract document text and split it into chunks."""
    text = extract_text(file_bytes, file_type)
    chunks = chunk_text(text, strategy)

    if not chunks:
        raise ValueError("Document produced no text chunks.")

    return chunks
