from sqlalchemy.orm import Session

from app.schemas.ask import AskRequest, AskResponse
from app.services.ask_service import AskService


class AgentOrchestrator:
    """Coordinates planner, retriever, generator, evaluator, and governance agents."""

    def __init__(self, ask_service: AskService) -> None:
        self.ask_service = ask_service

    def run(self, db: Session, request: AskRequest) -> AskResponse:
        return self.ask_service.ask(db, request)
