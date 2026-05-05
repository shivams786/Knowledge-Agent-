from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_services
from app.db.session import get_db
from app.services.audit_service import AuditService
from app.services.metrics_service import MetricsService

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    database_status = "ok"
    try:
        db.execute(text("select 1"))
    except Exception:
        database_status = "error"
    redis_status = "not_configured_local_check"
    return {"api_status": "ok", "database_status": database_status, "redis_status": redis_status, "vector_index_status": get_services()["vector_store"].status()}


@router.get("/metrics/basic")
def metrics_basic(db: Session = Depends(get_db)) -> dict:
    return MetricsService().basic(db)


@router.get("/audit-logs")
def audit_logs(limit: int = 50, db: Session = Depends(get_db)) -> list[dict]:
    return [{"id": row.id, "trace_id": row.trace_id, "event_type": row.event_type, "actor": row.actor, "payload_json": row.payload_json, "created_at": row.created_at} for row in AuditService().recent(db, limit)]
