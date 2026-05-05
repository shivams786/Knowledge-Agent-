from app.agents.governance import GovernanceAgent
from app.agents.query_planner import QueryPlannerAgent

from tests.conftest import upload_sample


def test_vector_keyword_and_hybrid_search(client):
    upload_sample(client)
    semantic = client.get("/search", params={"q": "citation governance", "search_mode": "semantic", "top_k": 3}).json()
    keyword = client.get("/search", params={"q": "citation governance", "search_mode": "keyword", "top_k": 3}).json()
    hybrid = client.get("/search", params={"q": "citation governance", "search_mode": "hybrid", "top_k": 3}).json()
    assert semantic["results"]
    assert keyword["results"]
    assert hybrid["results"][0]["hybrid_score"] >= 0


def test_tool_registry_and_tools(client):
    uploaded = upload_sample(client).json()
    document_id = uploaded["document"]["id"]
    tools = client.get("/tools").json()
    assert {"search_documents", "read_file", "create_ticket"} <= {tool["name"] for tool in tools}
    search = client.post("/tools/search_documents/execute", json={"arguments": {"query": "audit logs", "top_k": 2, "filters": {"access_level": "internal"}}}).json()
    read = client.post("/tools/read_file/execute", json={"arguments": {"document_id": document_id}}).json()
    ticket = client.post("/tools/create_ticket/execute", json={"arguments": {"title": "Fix retrieval", "description": "Ranking drift", "severity": "high", "tags": ["rag"]}}).json()
    assert search["success"] and search["result"]["results"]
    assert read["success"] and read["result"]["filename"] == "governance.md"
    assert ticket["success"] and ticket["result"]["ticket"]["status"] == "open"


def test_query_planner_agent():
    planner = QueryPlannerAgent()
    assert planner.plan("summarize this document").intent == "summarization"
    assert planner.plan("where is this python class").intent == "code_question"
    assert planner.plan("create a ticket").tools == ["create_ticket"]


def test_governance_citation_enforcement():
    gov = GovernanceAgent()
    assert gov.check("answer without citation", [], True)["status"] == "fail"


def test_access_level_filtering(client):
    upload_sample(client, name="secret.md", text="Restricted acquisition plan", access_level="restricted")
    public = client.get("/search", params={"q": "acquisition", "access_level": "internal"}).json()
    restricted = client.get("/search", params={"q": "acquisition", "access_level": "restricted"}).json()
    assert public["results"] == []
    assert restricted["results"]
