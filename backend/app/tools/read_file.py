from sqlalchemy.orm import Session

from app.services.document_service import DocumentService
from app.tools.base import Tool


class ReadFileTool(Tool):
    name = "read_file"
    description = "Read document metadata and extracted text by document id."
    input_schema = {"document_id": "integer"}
    output_schema = {"document": "DocumentDetail"}

    def __init__(self, documents: DocumentService) -> None:
        self.documents = documents

    def execute(self, db: Session, arguments: dict) -> dict:
        doc = self.documents.get_document(db, int(arguments["document_id"]))
        return {
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "source_path": doc.source_path,
            "checksum": doc.checksum,
            "access_level": doc.access_level,
            "created_at": doc.created_at.isoformat(),
            "extracted_content": doc.extracted_text,
        }
