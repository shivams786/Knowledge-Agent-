from datetime import datetime

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str
    description: str
    severity: str = "medium"
    tags: list[str] = Field(default_factory=list)


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: str | None = None
    status: str | None = None
    tags: list[str] | None = None


class TicketRead(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    status: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime
