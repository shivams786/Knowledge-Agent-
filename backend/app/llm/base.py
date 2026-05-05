from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    token_usage: dict[str, int] | None = None


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def generate(self, prompt: str, *, context: str | None = None) -> LLMResponse:
        raise NotImplementedError
