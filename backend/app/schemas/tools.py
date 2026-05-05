from typing import Any

from pydantic import BaseModel, Field


class ToolSpec(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


class ToolExecutionRequest(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolExecutionResponse(BaseModel):
    tool_name: str
    trace_id: str
    success: bool
    result: dict[str, Any] | list[Any] | str | None = None
    error: str | None = None
    latency_ms: int
