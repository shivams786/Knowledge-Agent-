import math
import re
from collections import Counter

from sqlalchemy.orm import Session

from app.db.models import Document, DocumentChunk


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


class KeywordSearch:
    """Simple BM25-like scorer that works across SQLite and PostgreSQL."""

    def search(self, db: Session, query: str, top_k: int, file_type: str | None = None, access_level: str | None = None) -> list[tuple[DocumentChunk, float]]:
        terms = tokenize(query)
        if not terms:
            return []
        rows = db.query(DocumentChunk).join(Document).all()
        rows = [row for row in rows if (not file_type or row.document.file_type == file_type) and (not access_level or row.document.access_level == access_level)]
        doc_freq = Counter()
        chunk_terms = {}
        for chunk in rows:
            tokens = tokenize(chunk.chunk_text)
            chunk_terms[chunk.id] = tokens
            unique = set(tokens)
            for term in set(terms):
                if term in unique:
                    doc_freq[term] += 1
        total = max(1, len(rows))
        scored: list[tuple[DocumentChunk, float]] = []
        for chunk in rows:
            tf = Counter(chunk_terms[chunk.id])
            length_norm = max(1.0, len(chunk_terms[chunk.id]) / 120)
            score = 0.0
            for term in terms:
                idf = math.log(1 + (total - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
                score += (tf[term] / length_norm) * idf
            if score > 0:
                scored.append((chunk, score))
        return sorted(scored, key=lambda item: item[1], reverse=True)[:top_k]
