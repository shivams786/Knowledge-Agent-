from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Enterprise Knowledge Agent Platform"
    environment: str = "local"
    database_url: str = "sqlite:///./enterprise_knowledge_agent.db"
    redis_url: str = "redis://redis:6379/0"
    upload_dir: Path = Field(default=Path("../data/uploads"))
    index_dir: Path = Field(default=Path("../data/indexes"))
    llm_provider: str = "mock"
    embedding_provider: str = "mock"
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 384
    chunk_size: int = 900
    chunk_overlap: int = 120


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.index_dir.mkdir(parents=True, exist_ok=True)
    return settings
