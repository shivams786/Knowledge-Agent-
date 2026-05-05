import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Ticket
from app.schemas.tickets import TicketCreate, TicketRead, TicketUpdate


def to_ticket_read(ticket: Ticket) -> TicketRead:
    return TicketRead(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        severity=ticket.severity,
        status=ticket.status,
        tags=json.loads(ticket.tags_json or "[]"),
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )


class TicketService:
    def create(self, db: Session, payload: TicketCreate) -> TicketRead:
        ticket = Ticket(title=payload.title, description=payload.description, severity=payload.severity, tags_json=json.dumps(payload.tags))
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return to_ticket_read(ticket)

    def list(self, db: Session) -> list[TicketRead]:
        return [to_ticket_read(ticket) for ticket in db.query(Ticket).order_by(Ticket.created_at.desc()).all()]

    def get(self, db: Session, ticket_id: int) -> Ticket:
        ticket = db.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket

    def update(self, db: Session, ticket_id: int, payload: TicketUpdate) -> TicketRead:
        ticket = self.get(db, ticket_id)
        updates = payload.model_dump(exclude_unset=True)
        if "tags" in updates:
            ticket.tags_json = json.dumps(updates.pop("tags"))
        for key, value in updates.items():
            setattr(ticket, key, value)
        db.commit()
        db.refresh(ticket)
        return to_ticket_read(ticket)
