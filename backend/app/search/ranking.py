from datetime import datetime, timezone


def recency_boost(created_at: datetime) -> float:
    age_days = max(0, (datetime.now(timezone.utc) - created_at.replace(tzinfo=timezone.utc)).days)
    return max(0.0, 0.08 * (1 - min(age_days, 365) / 365))


def hybrid_score(vector_score: float, keyword_score: float, created_at: datetime, mode: str) -> float:
    if mode == "semantic":
        return vector_score
    if mode == "keyword":
        return keyword_score
    normalized_keyword = min(1.0, keyword_score / 5.0)
    return (0.62 * vector_score) + (0.30 * normalized_keyword) + recency_boost(created_at)
