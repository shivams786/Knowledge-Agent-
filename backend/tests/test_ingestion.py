from pathlib import Path

from app.ingestion.chunker import TextChunker
from app.ingestion.embeddings import MockEmbeddingProvider
from app.ingestion.loaders import extract_text
from app.services.document_service import sha256_bytes


def test_checksum_duplicate_basis():
    assert sha256_bytes(b"same") == sha256_bytes(b"same")
    assert sha256_bytes(b"same") != sha256_bytes(b"different")


def test_text_extraction():
    path = Path("test_runtime") / "note.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Title\nGoverned RAG", encoding="utf-8")
    assert "Governed RAG" in extract_text(path)


def test_chunking_prose_and_code():
    prose_chunks = TextChunker(chunk_size=10, overlap=2).chunk(" ".join(["word"] * 25), 1, "doc.md")
    code_chunks = TextChunker(chunk_size=40, overlap=5).chunk("\n".join([f"line {i}" for i in range(50)]), 1, "app.py")
    assert len(prose_chunks) > 1
    assert code_chunks[0].metadata["start_line"] == 1
    assert prose_chunks[0].citation_id.startswith("[doc:1-chunk:0-")


def test_mock_embedding_generation():
    provider = MockEmbeddingProvider(16)
    vector = provider.embed_query("enterprise search")
    assert len(vector) == 16
    assert vector == provider.embed_query("enterprise search")
