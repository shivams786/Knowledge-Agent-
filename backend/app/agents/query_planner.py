from dataclasses import dataclass, field


@dataclass
class QueryPlan:
    intent: str
    tools: list[str] = field(default_factory=list)


class QueryPlannerAgent:
    """Classifies user intent and selects MCP-style tools."""

    def plan(self, query: str) -> QueryPlan:
        q = query.lower()
        if "ticket" in q or "bug" in q:
            return QueryPlan("ticket_creation", ["create_ticket"])
        if "pr summary" in q or "pull request" in q:
            return QueryPlan("pr_summary", ["generate_pr_summary"])
        if "summarize" in q or "summary" in q:
            return QueryPlan("summarization", ["summarize_document"])
        if any(word in q for word in ["function", "class", "method", "code", "python", "java", "typescript"]):
            return QueryPlan("code_question", ["search_codebase"])
        if q.strip():
            return QueryPlan("document_question", ["search_documents"])
        return QueryPlan("unsupported", [])
