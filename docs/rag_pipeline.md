# RAG Pipeline

The `/ask` endpoint runs five explicit agents:

1. Query planner classifies intent.
2. Retriever finds relevant chunks with semantic, keyword, or hybrid search.
3. Answer generator uses the LLM abstraction and retrieved context.
4. Evaluator computes confidence and hallucination risk.
5. Governance enforces citation and context rules.

The mock LLM provider is deterministic and keeps tests independent from paid APIs.
