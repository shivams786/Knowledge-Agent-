from sqlalchemy.orm import Session

from app.search.hybrid_search import HybridSearchService
from app.tools.base import Tool


class SearchDocumentsTool(Tool):
    name = "search_documents"
    description = "Search enterprise documents with semantic, keyword, or hybrid ranking and citation metadata."
    input_schema = {"query": "string", "top_k": "integer", "filters": {"file_type": "string?", "access_level": "string?", "search_mode": "string?"}}
    output_schema = {"results": "SearchResult[]"}

    def __init__(self, search_service: HybridSearchService) -> None:
        self.search_service = search_service

    def execute(self, db: Session, arguments: dict) -> dict:
        filters = arguments.get("filters") or {}
        results = self.search_service.search(
            db,
            arguments["query"],
            top_k=int(arguments.get("top_k", 5)),
            file_type=filters.get("file_type"),
            access_level=filters.get("access_level", "internal"),
            search_mode=filters.get("search_mode", "hybrid"),
        )
        return {"results": [result.model_dump() for result in results]}
