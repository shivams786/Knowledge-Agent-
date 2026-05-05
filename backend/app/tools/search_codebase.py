from sqlalchemy.orm import Session

from app.search.hybrid_search import HybridSearchService
from app.tools.base import Tool


class SearchCodebaseTool(Tool):
    name = "search_codebase"
    description = "Search code chunks with optional language filter and line hints."
    input_schema = {"query": "string", "language": "string?", "top_k": "integer"}
    output_schema = {"results": "CodeSearchResult[]"}

    def __init__(self, search_service: HybridSearchService) -> None:
        self.search_service = search_service

    def execute(self, db: Session, arguments: dict) -> dict:
        language = arguments.get("language")
        results = self.search_service.search(db, arguments["query"], top_k=int(arguments.get("top_k", 5)), file_type=language, access_level=arguments.get("access_level", "internal"), search_mode="hybrid")
        return {"results": [result.model_dump() for result in results]}
