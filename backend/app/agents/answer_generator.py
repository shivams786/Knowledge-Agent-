from app.llm.base import LLMProvider
from app.schemas.search import SearchResult


class AnswerGeneratorAgent:
    template_name = "grounded_rag_answer"
    version = "v1"

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def generate(self, question: str, chunks: list[SearchResult]) -> tuple[str, dict[str, int] | None]:
        context = "\n\n".join(f"{chunk.citation_id}\n{chunk.chunk_text}" for chunk in chunks)
        prompt = f"Question: {question}\nAnswer with citations and say when context is insufficient."
        response = self.llm.generate(prompt, context=context)
        return response.text, response.token_usage
