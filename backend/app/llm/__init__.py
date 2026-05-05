from app.core.config import get_settings
from app.llm.base import LLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.openai_provider import OpenAICompatibleProvider


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI LLM provider")
        return OpenAICompatibleProvider(settings.openai_api_key, settings.openai_base_url, settings.openai_model)
    return MockLLMProvider()
