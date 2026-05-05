from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    document_id: int
    chunk_id: int
    document_title: str
    chunk_text: str
    similarity_score: float = 0
    keyword_score: float = 0
    hybrid_score: float = 0
    citation_id: str
    source_filename: str
    file_type: str
    access_level: str


class SearchResponse(BaseModel):
    query: str
    search_mode: str
    top_k: int
    results: list[SearchResult] = Field(default_factory=list)
    trace_id: str
