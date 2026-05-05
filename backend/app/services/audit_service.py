import json
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AuditLog


class AuditService:
    def record(self, db: Session, trace_id: str, event_type: str, payload: dict[str, Any], actor: str = "system") -> AuditLog:
        entry = AuditLog(trace_id=trace_id, event_type=event_type, actor=actor, payload_json=json.dumps(payload, default=str))
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    def recent(self, db: Session, limit: int = 50) -> list[AuditLog]:
        return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
