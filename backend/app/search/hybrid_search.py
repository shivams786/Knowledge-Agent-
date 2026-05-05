from sqlalchemy.orm import Session

from app.core.security import can_access
from app.db.models import DocumentChunk
from app.ingestion.embeddings import EmbeddingProvider
from app.schemas.search import SearchResult
from app.search.keyword_search import KeywordSearch
from app.search.ranking import hybrid_score
from app.search.vector_store import FaissVectorStore


class HybridSearchService:
    def __init__(self, embeddings: EmbeddingProvider, vector_store: FaissVectorStore | None = None) -> None:
        self.embeddings = embeddings
        self.vector_store = vector_store or FaissVectorStore()
        self.keyword = KeywordSearch()

    def search(
        self,
        db: Session,
        query: str,
        top_k: int = 5,
        file_type: str | None = None,
        access_level: str | None = None,
        search_mode: str = "hybrid",
    ) -> list[SearchResult]:
        semantic_scores: dict[int, float] = {}
        if search_mode in {"semantic", "hybrid"}:
            for chunk_id, score in self.vector_store.search(self.embeddings.embed_query(query), top_k=max(top_k * 4, 10)):
                semantic_scores[chunk_id] = score

        keyword_scores: dict[int, float] = {}
        if search_mode in {"keyword", "hybrid"}:
            for chunk, score in self.keyword.search(db, query, top_k=max(top_k * 4, 10), file_type=file_type, access_level=None):
                keyword_scores[chunk.id] = score

        candidate_ids = set(semantic_scores) | set(keyword_scores)
        chunks = db.query(DocumentChunk).filter(DocumentChunk.id.in_(candidate_ids)).all() if candidate_ids else []
        results: list[SearchResult] = []
        for chunk in chunks:
            doc = chunk.document
            if file_type and doc.file_type != file_type:
                continue
            if not can_access(doc.access_level, access_level):
                continue
            vector_score = semantic_scores.get(chunk.id, 0.0)
            keyword_score_value = keyword_scores.get(chunk.id, 0.0)
            score = hybrid_score(vector_score, keyword_score_value, chunk.created_at, search_mode)
            results.append(
                SearchResult(
                    document_id=doc.id,
                    chunk_id=chunk.id,
                    document_title=doc.filename,
                    chunk_text=chunk.chunk_text,
                    similarity_score=round(vector_score, 4),
                    keyword_score=round(keyword_score_value, 4),
                    hybrid_score=round(score, 4),
                    citation_id=chunk.citation_id,
                    source_filename=doc.filename,
                    file_type=doc.file_type,
                    access_level=doc.access_level,
                )
            )
        return sorted(results, key=lambda row: row.hybrid_score, reverse=True)[:top_k]
