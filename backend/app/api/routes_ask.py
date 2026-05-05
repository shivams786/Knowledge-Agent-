from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_services
from app.db.session import get_db
from app.schemas.ask import AskRequest, AskResponse

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, db: Session = Depends(get_db)) -> AskResponse:
    return get_services()["ask"].ask(db, request)
