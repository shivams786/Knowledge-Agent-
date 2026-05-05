from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_services
from app.core.telemetry import new_trace_id
from app.db.session import get_db
from app.schemas.search import SearchResponse
from app.services.audit_service import AuditService

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
def search(q: str, top_k: int = Query(5, ge=1, le=50), file_type: str | None = None, access_level: str | None = "internal", search_mode: str = "hybrid", db: Session = Depends(get_db)) -> SearchResponse:
    trace_id = new_trace_id()
    results = get_services()["search"].search(db, q, top_k=top_k, file_type=file_type, access_level=access_level, search_mode=search_mode)
    AuditService().record(db, trace_id, "search_query", {"query": q, "top_k": top_k, "result_count": len(results)})
    return SearchResponse(query=q, search_mode=search_mode, top_k=top_k, results=results, trace_id=trace_id)
