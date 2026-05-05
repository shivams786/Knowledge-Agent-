# Architecture

The system is backend-first. FastAPI exposes REST endpoints, SQLAlchemy persists metadata and operational logs, FAISS stores local vectors, and Streamlit consumes the public API.

Core boundaries:

- Ingestion owns file extraction, checksums, chunking, embeddings, metadata persistence, and vector writes.
- Search owns vector retrieval, keyword scoring, hybrid ranking, and access filtering.
- Agents own the RAG workflow and make the behavior easy to explain.
- Tools expose MCP-style capabilities through a registry and execution endpoint.
- Services own transactional business operations such as documents, tickets, audit logs, and metrics.
