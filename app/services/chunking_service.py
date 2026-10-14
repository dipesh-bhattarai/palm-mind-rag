
from typing import Literal

ChunkingStrategy = Literal["fixed_size", "recursive"]

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def fixed_size_chunk(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into fixed-size overlapping character chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size.")

    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap

    for start in range(0, len(text), step):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)

        if start + chunk_size >= len(text):
            break

    return chunks


def recursive_chunk(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text while prioritizing paragraph and sentence boundaries."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size.")

    text = text.strip()
    if not text:
        return []

    separators = ["\n\n", "\n", ". ", "? ", "! ", " "]
    chunks: list[str] = []
    current = ""

    def split_long_piece(piece: str) -> list[str]:
        if len(piece) <= chunk_size:
            return [piece]

        pieces: list[str] = []
        start = 0
        step = chunk_size - overlap

        while start < len(piece):
            pieces.append(piece[start : start + chunk_size])
            start += step

        return pieces

    def process_piece(piece: str, separator_index: int = 0) -> None:
        nonlocal current

        piece = piece.strip()
        if not piece:
            return

        if len(piece) > chunk_size and separator_index < len(separators):
            separator = separators[separator_index]
            parts = piece.split(separator)

            if len(parts) > 1:
                for index, part in enumerate(parts):
                    if index < len(parts) - 1:
                        part += separator
                    process_piece(part, separator_index + 1)
                return

        if len(piece) > chunk_size:
            for part in split_long_piece(piece):
                process_piece(part, len(separators))
            return

        candidate = f"{current}\n{piece}".strip() if current else piece

        if len(candidate) <= chunk_size:
            current = candidate
            return

        if current:
            chunks.append(current)
            previous = current
            current = (
                previous[-overlap:].strip()
                if overlap
                else ""
            )

        candidate = f"{current}\n{piece}".strip() if current else piece

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            process_piece(piece, separator_index + 1)

    process_piece(text)

    if current:
        chunks.append(current)

    return chunks


def chunk_text(
    text: str,
    strategy: ChunkingStrategy,
) -> list[str]:
    """Dispatch text to the requested chunking strategy."""
    if strategy == "fixed_size":
        return fixed_size_chunk(text)

    if strategy == "recursive":
        return recursive_chunk(text)

    raise ValueError(f"Unsupported chunking strategy: {strategy}")
