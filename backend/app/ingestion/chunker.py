import hashlib
from dataclasses import dataclass, field

from app.ingestion.loaders import is_code_file


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    text: str
    citation_id: str
    metadata: dict[str, int | str] = field(default_factory=dict)


class TextChunker:
    """Metadata-preserving chunker with different boundaries for prose and code."""

    def __init__(self, chunk_size: int = 900, overlap: int = 120) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, document_id: int, filename: str) -> list[TextChunk]:
        if not text.strip():
            return []
        return self._chunk_code(text, document_id, filename) if is_code_file(filename) else self._chunk_prose(text, document_id, filename)

    def _chunk_prose(self, text: str, document_id: int, filename: str) -> list[TextChunk]:
        words = text.split()
        chunks: list[TextChunk] = []
        step = max(1, self.chunk_size - self.overlap)
        for index, start in enumerate(range(0, len(words), step)):
            piece = " ".join(words[start : start + self.chunk_size]).strip()
            if piece:
                chunks.append(self._make_chunk(index, piece, document_id, filename, {"start_word": start}))
            if start + self.chunk_size >= len(words):
                break
        return chunks

    def _chunk_code(self, text: str, document_id: int, filename: str) -> list[TextChunk]:
        lines = text.splitlines()
        target_lines = max(20, self.chunk_size // 12)
        overlap_lines = max(3, self.overlap // 20)
        step = max(1, target_lines - overlap_lines)
        chunks: list[TextChunk] = []
        for index, start in enumerate(range(0, len(lines), step)):
            selected = lines[start : start + target_lines]
            if selected:
                metadata = {"start_line": start + 1, "end_line": start + len(selected)}
                chunks.append(self._make_chunk(index, "\n".join(selected), document_id, filename, metadata))
            if start + target_lines >= len(lines):
                break
        return chunks

    def _make_chunk(self, index: int, text: str, document_id: int, filename: str, metadata: dict[str, int | str]) -> TextChunk:
        digest = hashlib.sha1(f"{document_id}:{filename}:{index}:{text[:80]}".encode("utf-8")).hexdigest()[:10]
        citation_id = f"[doc:{document_id}-chunk:{index}-{digest}]"
        return TextChunk(chunk_index=index, text=text, citation_id=citation_id, metadata=metadata)
