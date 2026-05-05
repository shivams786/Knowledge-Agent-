from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_services
from app.core.telemetry import new_trace_id
from app.db.session import get_db
from app.schemas.documents import DocumentDetail, DocumentRead, UploadResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
def upload_document(file: UploadFile = File(...), access_level: str = Form("internal"), db: Session = Depends(get_db)) -> UploadResponse:
    doc, count, duplicate = get_services()["documents"].ingest_upload(db, file, access_level)
    AuditService().record(db, new_trace_id(), "uploaded_document", {"document_id": doc.id, "filename": doc.filename, "duplicate": duplicate})
    return UploadResponse(document=DocumentRead.model_validate(doc), chunk_count=count, duplicate=duplicate, message="Duplicate document reused" if duplicate else "Document ingested")


@router.get("", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db)) -> list[DocumentRead]:
    return [DocumentRead.model_validate(doc) for doc in get_services()["documents"].list_documents(db)]


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(document_id: int, db: Session = Depends(get_db)) -> DocumentDetail:
    return DocumentDetail.model_validate(get_services()["documents"].get_document(db, document_id))
