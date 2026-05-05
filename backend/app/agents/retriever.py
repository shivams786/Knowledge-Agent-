from sqlalchemy.orm import Session

from app.schemas.search import SearchResult
from app.search.hybrid_search import HybridSearchService


class RetrieverAgent:
    def __init__(self, search_service: HybridSearchService) -> None:
        self.search_service = search_service

    def retrieve(self, db: Session, query: str, top_k: int, search_mode: str, access_level: str | None, file_type: str | None = None) -> list[SearchResult]:
        return self.search_service.search(db, query, top_k=top_k, search_mode=search_mode, access_level=access_level, file_type=file_type)
