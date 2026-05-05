import io
from uuid import uuid4
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_services
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.ingestion.embeddings import MockEmbeddingProvider
from app.main import app
from app.search.hybrid_search import HybridSearchService
from app.search.vector_store import FaissVectorStore
from app.services.document_service import DocumentService
from app.services.ticket_service import TicketService
from app.llm.mock_provider import MockLLMProvider
from app.agents.query_planner import QueryPlannerAgent
from app.agents.retriever import RetrieverAgent
from app.agents.answer_generator import AnswerGeneratorAgent
from app.agents.evaluator import EvaluatorAgent
from app.agents.governance import GovernanceAgent
from app.services.ask_service import AskService
from app.tools.registry import ToolRegistry
from app.tools.search_documents import SearchDocumentsTool
from app.tools.read_file import ReadFileTool
from app.tools.create_ticket import CreateTicketTool
from app.tools.summarize_document import SummarizeDocumentTool
from app.tools.generate_pr_summary import GeneratePRSummaryTool
from app.tools.search_codebase import SearchCodebaseTool


@pytest.fixture()
def temp_services(monkeypatch):
    settings = get_settings()
    runtime = Path("test_runtime") / uuid4().hex
    settings.upload_dir = runtime / "uploads"
    settings.index_dir = runtime / "indexes"
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.index_dir.mkdir(parents=True, exist_ok=True)
    embeddings = MockEmbeddingProvider(settings.embedding_dimension)
    vector_store = FaissVectorStore(index_path=settings.index_dir / "test.index")
    search = HybridSearchService(embeddings, vector_store)
    documents = DocumentService(embeddings, vector_store)
    tickets = TicketService()
    llm = MockLLMProvider()
    registry = ToolRegistry()
    registry.register(SearchDocumentsTool(search))
    registry.register(ReadFileTool(documents))
    registry.register(SummarizeDocumentTool(documents, llm))
    registry.register(CreateTicketTool(tickets))
    registry.register(GeneratePRSummaryTool(llm))
    registry.register(SearchCodebaseTool(search))
    ask = AskService(QueryPlannerAgent(), RetrieverAgent(search), AnswerGeneratorAgent(llm), EvaluatorAgent(), GovernanceAgent())
    services = {"embeddings": embeddings, "vector_store": vector_store, "search": search, "documents": documents, "tickets": tickets, "llm": llm, "tools": registry, "ask": ask}
    get_services.cache_clear()
    monkeypatch.setattr("app.api.dependencies.get_services", lambda: services)
    monkeypatch.setattr("app.api.routes_documents.get_services", lambda: services)
    monkeypatch.setattr("app.api.routes_search.get_services", lambda: services)
    monkeypatch.setattr("app.api.routes_ask.get_services", lambda: services)
    monkeypatch.setattr("app.api.routes_tools.get_services", lambda: services)
    monkeypatch.setattr("app.api.routes_tickets.get_services", lambda: services)
    monkeypatch.setattr("app.api.routes_health.get_services", lambda: services)
    return services


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session, temp_services):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def upload_sample(client, name="governance.md", text=None, access_level="internal"):
    content = text or "Enterprise governance requires citation grounded answers and audit logs for every ask query. Hybrid search combines semantic and keyword ranking."
    return client.post("/documents/upload", files={"file": (name, io.BytesIO(content.encode()), "text/markdown")}, data={"access_level": access_level})
