from functools import lru_cache

from app.agents.answer_generator import AnswerGeneratorAgent
from app.agents.evaluator import EvaluatorAgent
from app.agents.governance import GovernanceAgent
from app.agents.query_planner import QueryPlannerAgent
from app.agents.retriever import RetrieverAgent
from app.ingestion.embeddings import get_embedding_provider
from app.llm import get_llm_provider
from app.search.hybrid_search import HybridSearchService
from app.search.vector_store import FaissVectorStore
from app.services.ask_service import AskService
from app.services.document_service import DocumentService
from app.services.ticket_service import TicketService
from app.tools.create_ticket import CreateTicketTool
from app.tools.generate_pr_summary import GeneratePRSummaryTool
from app.tools.read_file import ReadFileTool
from app.tools.registry import ToolRegistry
from app.tools.search_codebase import SearchCodebaseTool
from app.tools.search_documents import SearchDocumentsTool
from app.tools.summarize_document import SummarizeDocumentTool


@lru_cache
def get_services() -> dict:
    embeddings = get_embedding_provider()
    vector_store = FaissVectorStore()
    search = HybridSearchService(embeddings, vector_store)
    documents = DocumentService(embeddings, vector_store)
    tickets = TicketService()
    llm = get_llm_provider()
    registry = ToolRegistry()
    registry.register(SearchDocumentsTool(search))
    registry.register(ReadFileTool(documents))
    registry.register(SummarizeDocumentTool(documents, llm))
    registry.register(CreateTicketTool(tickets))
    registry.register(GeneratePRSummaryTool(llm))
    registry.register(SearchCodebaseTool(search))
    ask = AskService(QueryPlannerAgent(), RetrieverAgent(search), AnswerGeneratorAgent(llm), EvaluatorAgent(), GovernanceAgent())
    return {"embeddings": embeddings, "vector_store": vector_store, "search": search, "documents": documents, "tickets": tickets, "llm": llm, "tools": registry, "ask": ask}
