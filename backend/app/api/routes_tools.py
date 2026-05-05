import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_services
from app.core.telemetry import new_trace_id
from app.db.session import get_db
from app.schemas.tools import ToolExecutionRequest, ToolExecutionResponse, ToolSpec
from app.services.audit_service import AuditService
from app.tools.base import timed_execute

router = APIRouter(prefix="/tools", tags=["tools"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[ToolSpec])
def list_tools() -> list[ToolSpec]:
    return [ToolSpec(**spec) for spec in get_services()["tools"].list()]


@router.post("/{tool_name}/execute", response_model=ToolExecutionResponse)
def execute_tool(tool_name: str, request: ToolExecutionRequest, db: Session = Depends(get_db)) -> ToolExecutionResponse:
    trace_id = new_trace_id()
    tool = get_services()["tools"].get(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    try:
        result, latency_ms = timed_execute(tool, db, request.arguments)
        AuditService().record(db, trace_id, "tool_execution", {"tool_name": tool_name, "success": True})
        logger.info("tool_call", extra={"eka_trace_id": trace_id, "eka_tool_name": tool_name, "eka_input_summary": str(request.arguments)[:300], "eka_success": True, "eka_latency_ms": latency_ms})
        return ToolExecutionResponse(tool_name=tool_name, trace_id=trace_id, success=True, result=result, latency_ms=latency_ms)
    except Exception as exc:
        AuditService().record(db, trace_id, "tool_execution", {"tool_name": tool_name, "success": False, "error": str(exc)})
        logger.info("tool_call", extra={"eka_trace_id": trace_id, "eka_tool_name": tool_name, "eka_input_summary": str(request.arguments)[:300], "eka_success": False, "eka_latency_ms": 0})
        return ToolExecutionResponse(tool_name=tool_name, trace_id=trace_id, success=False, error=str(exc), latency_ms=0)
