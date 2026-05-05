from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.db.models import Document
from app.services.document_service import DocumentService


class IngestionPipeline:
    """Thin pipeline facade for interview-friendly ingestion orchestration."""

    def __init__(self, documents: DocumentService) -> None:
        self.documents = documents

    def run(self, db: Session, upload: UploadFile, access_level: str) -> tuple[Document, int, bool]:
        return self.documents.ingest_upload(db, upload, access_level)
