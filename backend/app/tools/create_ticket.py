from sqlalchemy.orm import Session

from app.schemas.tickets import TicketCreate
from app.services.ticket_service import TicketService
from app.tools.base import Tool


class CreateTicketTool(Tool):
    name = "create_ticket"
    description = "Create an internal enterprise ticket in PostgreSQL."
    input_schema = {"title": "string", "description": "string", "severity": "low|medium|high|critical", "tags": "string[]"}
    output_schema = {"ticket": "Ticket"}

    def __init__(self, tickets: TicketService) -> None:
        self.tickets = tickets

    def execute(self, db: Session, arguments: dict) -> dict:
        ticket = self.tickets.create(db, TicketCreate(**arguments))
        return {"ticket": ticket.model_dump(mode="json")}
