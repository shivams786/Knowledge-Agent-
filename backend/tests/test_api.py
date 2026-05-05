from tests.conftest import upload_sample


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["api_status"] == "ok"


def test_upload_duplicate_detection(client):
    first = upload_sample(client)
    second = upload_sample(client)
    assert first.status_code == 200
    assert second.json()["duplicate"] is True


def test_search_endpoint(client):
    upload_sample(client)
    response = client.get("/search", params={"q": "hybrid search", "top_k": 2})
    assert response.status_code == 200
    assert response.json()["results"]


def test_ask_endpoint_with_mock_llm(client):
    upload_sample(client)
    response = client.post("/ask", json={"user_query": "How does governance work?", "top_k": 3, "search_mode": "hybrid", "access_level": "internal"})
    payload = response.json()
    assert response.status_code == 200
    assert payload["citations"]
    assert payload["governance_status"] == "pass"
    assert payload["trace_id"]


def test_ticket_apis(client):
    created = client.post("/tickets", json={"title": "Investigate RAG", "description": "Search quality issue", "severity": "medium", "tags": ["search"]})
    assert created.status_code == 200
    ticket_id = created.json()["id"]
    assert client.get("/tickets").json()
    assert client.get(f"/tickets/{ticket_id}").json()["title"] == "Investigate RAG"
    updated = client.patch(f"/tickets/{ticket_id}", json={"status": "resolved"}).json()
    assert updated["status"] == "resolved"


def test_metrics_and_audit(client):
    upload_sample(client)
    client.get("/search", params={"q": "audit"})
    assert "total_documents" in client.get("/metrics/basic").json()
    assert client.get("/audit-logs").json()
