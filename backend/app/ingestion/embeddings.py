import hashlib
import math
from abc import ABC, abstractmethod

import httpx

from app.core.config import get_settings


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic hashing embedding suitable for tests and local demos."""

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[idx] += sign
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI-compatible embedding provider using the /embeddings endpoint."""

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = httpx.post(
            f"{self.base_url}/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "input": texts},
            timeout=30,
        )
        response.raise_for_status()
        return [item["embedding"] for item in response.json()["data"]]


def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    if settings.embedding_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI embeddings")
        return OpenAIEmbeddingProvider(settings.openai_api_key, settings.openai_base_url, settings.openai_embedding_model)
    return MockEmbeddingProvider(settings.embedding_dimension)
