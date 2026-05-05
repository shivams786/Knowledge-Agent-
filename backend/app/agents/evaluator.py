import re

from app.schemas.search import SearchResult


class EvaluatorAgent:
    def evaluate(self, answer: str, chunks: list[SearchResult]) -> dict[str, float | str]:
        citations = set(re.findall(r"\[doc:[^\]]+\]", answer))
        expected = {chunk.citation_id for chunk in chunks}
        coverage = len(citations & expected) / max(1, len(expected))
        relevance = sum(chunk.hybrid_score for chunk in chunks) / max(1, len(chunks))
        completeness = 0.8 if len(answer.split()) > 20 else 0.45
        confidence = max(0.0, min(1.0, (coverage * 0.45) + (min(1.0, relevance) * 0.35) + (completeness * 0.2)))
        risk = "low" if confidence >= 0.7 and citations else "medium" if chunks else "high"
        return {"confidence_score": round(confidence, 3), "hallucination_risk": risk, "citation_coverage": round(coverage, 3)}
