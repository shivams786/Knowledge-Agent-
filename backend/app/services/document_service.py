import hashlib
import json
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Document, DocumentChunk
from app.ingestion.chunker import TextChunker
from app.ingestion.embeddings import EmbeddingProvider
from app.ingestion.loaders import detect_file_type, extract_text, pretty_json_if_needed
from app.search.vector_store import FaissVectorStore


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class DocumentService:
    def __init__(self, embeddings: EmbeddingProvider, vector_store: FaissVectorStore | None = None) -> None:
        self.settings = get_settings()
        self.embeddings = embeddings
        self.vector_store = vector_store or FaissVectorStore()
        self.chunker = TextChunker(self.settings.chunk_size, self.settings.chunk_overlap)

    def ingest_upload(self, db: Session, upload: UploadFile, access_level: str = "internal") -> tuple[Document, int, bool]:
        data = upload.file.read()
        checksum = sha256_bytes(data)
        existing = db.query(Document).filter(Document.checksum == checksum).first()
        if existing:
            return existing, len(existing.chunks), True

        safe_name = Path(upload.filename or "upload.txt").name
        destination = self.settings.upload_dir / f"{checksum[:12]}_{safe_name}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        text = pretty_json_if_needed(safe_name, extract_text(destination))
        if not text.strip():
            raise HTTPException(status_code=400, detail="No extractable text found")
        doc = Document(
            filename=safe_name,
            file_type=detect_file_type(safe_name),
            source_path=str(destination),
            checksum=checksum,
            access_level=access_level,
            extracted_text=text,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        chunks = self.chunker.chunk(text, doc.id, safe_name)
        rows: list[DocumentChunk] = []
        for chunk in chunks:
            row = DocumentChunk(
                document_id=doc.id,
                chunk_index=chunk.chunk_index,
                chunk_text=chunk.text,
                citation_id=chunk.citation_id,
                token_count=len(chunk.text.split()),
                metadata_json=json.dumps(chunk.metadata),
            )
            db.add(row)
            rows.append(row)
        db.commit()
        for row in rows:
            db.refresh(row)
        self.vector_store.add([row.id for row in rows], self.embeddings.embed_texts([row.chunk_text for row in rows]))
        return doc, len(rows), False

    def list_documents(self, db: Session) -> list[Document]:
        return db.query(Document).order_by(Document.created_at.desc()).all()

    def get_document(self, db: Session, document_id: int) -> Document:
        doc = db.get(Document, document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc
