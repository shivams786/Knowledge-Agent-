from sqlalchemy.orm import Session

from app.llm.base import LLMProvider
from app.services.document_service import DocumentService
from app.tools.base import Tool


class SummarizeDocumentTool(Tool):
    name = "summarize_document"
    description = "Summarize a document with key points and chunk citations."
    input_schema = {"document_id": "integer"}
    output_schema = {"summary": "string", "citations": "string[]"}

    def __init__(self, documents: DocumentService, llm: LLMProvider) -> None:
        self.documents = documents
        self.llm = llm

    def execute(self, db: Session, arguments: dict) -> dict:
        doc = self.documents.get_document(db, int(arguments["document_id"]))
        citations = [chunk.citation_id for chunk in doc.chunks[:5]]
        context = "\n".join(f"{chunk.citation_id}\n{chunk.chunk_text[:800]}" for chunk in doc.chunks[:5])
        response = self.llm.generate(f"Summarize {doc.filename} with cited key points.", context=context)
        return {"summary": response.text, "citations": citations}
