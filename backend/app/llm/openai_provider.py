import httpx

from app.llm.base import LLMProvider, LLMResponse


class OpenAICompatibleProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, prompt: str, *, context: str | None = None) -> LLMResponse:
        messages = [
            {"role": "system", "content": "Answer only from provided context. Include citations exactly as given."},
            {"role": "user", "content": f"Context:\n{context or ''}\n\nQuestion:\n{prompt}"},
        ]
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "messages": messages, "temperature": 0.1},
            timeout=45,
        )
        response.raise_for_status()
        payload = response.json()
        return LLMResponse(payload["choices"][0]["message"]["content"], payload.get("usage"))
