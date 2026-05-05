import logging
import time

from sqlalchemy.orm import Session

from app.agents.answer_generator import AnswerGeneratorAgent
from app.agents.evaluator import EvaluatorAgent
from app.agents.governance import GovernanceAgent
from app.agents.query_planner import QueryPlannerAgent
from app.agents.retriever import RetrieverAgent
from app.core.telemetry import new_trace_id
from app.db.models import PromptVersion, QueryLog
from app.schemas.ask import AskRequest, AskResponse, Citation
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class AskService:
    def __init__(self, planner: QueryPlannerAgent, retriever: RetrieverAgent, generator: AnswerGeneratorAgent, evaluator: EvaluatorAgent, governance: GovernanceAgent) -> None:
        self.planner = planner
        self.retriever = retriever
        self.generator = generator
        self.evaluator = evaluator
        self.governance = governance
        self.audit = AuditService()

    def ask(self, db: Session, request: AskRequest) -> AskResponse:
        start = time.perf_counter()
        trace_id = new_trace_id()
        plan = self.planner.plan(request.user_query)
        chunks = self.retriever.retrieve(db, request.user_query, request.top_k, request.search_mode, request.access_level)
        if not chunks:
            answer = "I do not have enough context to answer this question with citations."
            token_usage = None
        else:
            answer, token_usage = self.generator.generate(request.user_query, chunks)
        evaluation = self.evaluator.evaluate(answer, chunks)
        governance = self.governance.check(answer, chunks, request.require_citations)
        latency_ms = int((time.perf_counter() - start) * 1000)

        if governance["status"] != "pass":
            self.audit.record(db, trace_id, "governance_failure", {"reason": governance["reason"], "query": request.user_query})
        self.audit.record(db, trace_id, "ask_query", {"query": request.user_query, "intent": plan.intent, "chunks": len(chunks)})
        db.add(PromptVersion(agent_name="AnswerGeneratorAgent", template_name=self.generator.template_name, version=self.generator.version, template_text="grounded citation answer"))
        db.add(QueryLog(trace_id=trace_id, user_query=request.user_query, search_mode=request.search_mode, retrieved_chunk_count=len(chunks), latency_ms=latency_ms, hallucination_risk=str(evaluation["hallucination_risk"]), governance_status=str(governance["status"])))
        db.commit()
        logger.info(
            "ask_request",
            extra={
                "eka_trace_id": trace_id,
                "eka_user_query": request.user_query,
                "eka_search_mode": request.search_mode,
                "eka_top_k": request.top_k,
                "eka_retrieved_chunk_count": len(chunks),
                "eka_retrieval_scores": [chunk.hybrid_score for chunk in chunks],
                "eka_latency_ms": latency_ms,
                "eka_llm_provider": self.generator.llm.name,
                "eka_token_usage": token_usage,
                "eka_hallucination_risk": evaluation["hallucination_risk"],
                "eka_governance_status": governance["status"],
            },
        )
        return AskResponse(
            final_answer=answer,
            citations=[Citation(citation_id=chunk.citation_id, document_id=chunk.document_id, source_filename=chunk.source_filename, snippet=chunk.chunk_text[:240]) for chunk in chunks if chunk.citation_id in answer],
            retrieved_chunks=chunks,
            confidence_score=float(evaluation["confidence_score"]),
            hallucination_risk=str(evaluation["hallucination_risk"]),
            governance_status=str(governance["status"]),
            latency_ms=latency_ms,
            trace_id=trace_id,
        )
