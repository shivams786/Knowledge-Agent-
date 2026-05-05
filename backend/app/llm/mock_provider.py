import re

from app.llm.base import LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    """Deterministic answer generator for local runs, tests, and CI."""

    name = "mock"

    def generate(self, prompt: str, *, context: str | None = None) -> LLMResponse:
        citations = re.findall(r"\[doc:[^\]]+\]", context or prompt)
        if not context or not citations:
            return LLMResponse("I do not have enough context to answer this question with citations.", {"prompt_tokens": len(prompt.split()), "completion_tokens": 12})
        snippets = [line.strip() for line in (context or "").splitlines() if line.strip() and not line.startswith("[doc:")]
        summary = " ".join(snippets[:2])[:700]
        unique_citations = " ".join(dict.fromkeys(citations))
        return LLMResponse(f"Based on the retrieved enterprise knowledge, {summary} {unique_citations}", {"prompt_tokens": len(prompt.split()), "completion_tokens": len(summary.split())})
