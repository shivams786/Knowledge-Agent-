import time
from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Session


class Tool(ABC):
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]

    @abstractmethod
    def execute(self, db: Session, arguments: dict[str, Any]) -> dict[str, Any] | list[Any] | str:
        raise NotImplementedError

    def spec(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "input_schema": self.input_schema, "output_schema": self.output_schema}


def timed_execute(tool: Tool, db: Session, arguments: dict[str, Any]) -> tuple[dict[str, Any] | list[Any] | str, int]:
    start = time.perf_counter()
    result = tool.execute(db, arguments)
    return result, int((time.perf_counter() - start) * 1000)
