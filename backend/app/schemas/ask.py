from pydantic import BaseModel, Field

from app.schemas.search import SearchResult


class AskRequest(BaseModel):
    user_query: str
    top_k: int = Field(default=5, ge=1, le=20)
    search_mode: str = "hybrid"
    access_level: str | None = "internal"
    require_citations: bool = True


class Citation(BaseModel):
    citation_id: str
    document_id: int
    source_filename: str
    snippet: str


class AskResponse(BaseModel):
    final_answer: str
    citations: list[Citation]
    retrieved_chunks: list[SearchResult]
    confidence_score: float
    hallucination_risk: str
    governance_status: str
    latency_ms: int
    trace_id: str
