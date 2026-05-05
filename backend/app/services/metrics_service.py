from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import AuditLog, Document, DocumentChunk, QueryLog, Ticket


class MetricsService:
    def basic(self, db: Session) -> dict[str, float | int]:
        total_queries = db.query(func.count(QueryLog.id)).scalar() or 0
        failed_queries = db.query(func.count(QueryLog.id)).filter(QueryLog.governance_status != "pass").scalar() or 0
        avg_latency = db.query(func.avg(QueryLog.latency_ms)).scalar() or 0
        governance_failures = db.query(func.count(AuditLog.id)).filter(AuditLog.event_type == "governance_failure").scalar() or 0
        return {
            "total_documents": db.query(func.count(Document.id)).scalar() or 0,
            "total_chunks": db.query(func.count(DocumentChunk.id)).scalar() or 0,
            "total_queries": total_queries,
            "failed_queries": failed_queries,
            "average_latency": round(float(avg_latency), 2),
            "total_tickets": db.query(func.count(Ticket.id)).scalar() or 0,
            "governance_failures": governance_failures,
        }
