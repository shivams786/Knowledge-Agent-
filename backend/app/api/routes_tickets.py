from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_services
from app.core.telemetry import new_trace_id
from app.db.session import get_db
from app.schemas.tickets import TicketCreate, TicketRead, TicketUpdate
from app.services.audit_service import AuditService
from app.services.ticket_service import to_ticket_read

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketRead)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)) -> TicketRead:
    ticket = get_services()["tickets"].create(db, payload)
    AuditService().record(db, new_trace_id(), "ticket_creation", {"ticket_id": ticket.id, "title": ticket.title})
    return ticket


@router.get("", response_model=list[TicketRead])
def list_tickets(db: Session = Depends(get_db)) -> list[TicketRead]:
    return get_services()["tickets"].list(db)


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)) -> TicketRead:
    return to_ticket_read(get_services()["tickets"].get(db, ticket_id))


@router.patch("/{ticket_id}", response_model=TicketRead)
def update_ticket(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)) -> TicketRead:
    return get_services()["tickets"].update(db, ticket_id, payload)
