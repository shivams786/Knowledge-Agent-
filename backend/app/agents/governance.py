import re

from app.schemas.search import SearchResult


class GovernanceAgent:
    def check(self, answer: str, chunks: list[SearchResult], require_citations: bool = True) -> dict[str, str | bool]:
        if not chunks:
            return {"status": "fail", "reason": "no_retrieved_context", "allowed": False}
        citations = re.findall(r"\[doc:[^\]]+\]", answer)
        if require_citations and not citations:
            return {"status": "fail", "reason": "missing_citations", "allowed": False}
        if any(chunk.access_level == "restricted" for chunk in chunks):
            return {"status": "warn", "reason": "restricted_context_used", "allowed": True}
        return {"status": "pass", "reason": "grounded_answer", "allowed": True}
