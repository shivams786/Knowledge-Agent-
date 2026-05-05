import json
from pathlib import Path

import numpy as np

try:
    import faiss
except Exception:  # pragma: no cover
    faiss = None

from app.core.config import get_settings


class FaissVectorStore:
    """Local FAISS vector index with a portable JSON metadata sidecar."""

    def __init__(self, dimension: int | None = None, index_path: Path | None = None) -> None:
        settings = get_settings()
        self.dimension = dimension or settings.embedding_dimension
        self.index_path = index_path or settings.index_dir / "faiss.index"
        self.meta_path = self.index_path.with_suffix(".json")
        self.vectors_path = self.index_path.with_suffix(".vectors.json")
        self._ids: list[int] = []
        self._vectors: list[list[float]] = []
        self.index = self._load_or_create()

    def _load_or_create(self):
        if faiss is None:
            return None
        if self.index_path.exists() and self.meta_path.exists():
            index = faiss.read_index(str(self.index_path))
            self._ids = json.loads(self.meta_path.read_text())
            if self.vectors_path.exists():
                self._vectors = json.loads(self.vectors_path.read_text())
            return index
        return faiss.IndexFlatIP(self.dimension)

    def add(self, chunk_ids: list[int], vectors: list[list[float]]) -> None:
        if not vectors:
            return
        arr = np.array(vectors, dtype="float32")
        self._vectors.extend(vectors)
        if faiss is None:
            self._ids.extend(chunk_ids)
            self._persist()
            return
        self.index.add(arr)
        self._ids.extend(chunk_ids)
        self._persist()

    def search(self, query_vector: list[float], top_k: int = 5) -> list[tuple[int, float]]:
        if not self._ids:
            return []
        if faiss is None:
            query = np.array(query_vector, dtype="float32")
            scored = []
            for chunk_id, vector in zip(self._ids, self._vectors):
                score = float(np.dot(query, np.array(vector, dtype="float32")))
                scored.append((chunk_id, score))
            return sorted(scored, key=lambda item: item[1], reverse=True)[:top_k]
        arr = np.array([query_vector], dtype="float32")
        scores, positions = self.index.search(arr, min(top_k, len(self._ids)))
        results: list[tuple[int, float]] = []
        for pos, score in zip(positions[0], scores[0]):
            if pos >= 0 and pos < len(self._ids):
                results.append((self._ids[pos], float(score)))
        return results

    def status(self) -> dict[str, int | bool]:
        return {"available": faiss is not None, "vector_count": len(self._ids), "dimension": self.dimension}

    def _persist(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.meta_path.write_text(json.dumps(self._ids))
        self.vectors_path.write_text(json.dumps(self._vectors))
        if faiss is not None and self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
