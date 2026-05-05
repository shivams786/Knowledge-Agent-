import streamlit as st

from _client import post

st.title("Ask Knowledge Agent")
question = st.text_area("Question")
left, mid, right = st.columns(3)
search_mode = left.selectbox("Search mode", ["hybrid", "semantic", "keyword"])
top_k = mid.slider("Top K", 1, 20, 5)
access_level = right.selectbox("Access level", ["public", "internal", "restricted"], index=1)
if st.button("Ask", type="primary", disabled=not question.strip()):
    result = post("/ask", json={"user_query": question, "search_mode": search_mode, "top_k": top_k, "access_level": access_level, "require_citations": True})
    st.subheader("Answer")
    st.write(result["final_answer"])
    st.metric("Confidence", result["confidence_score"])
    st.metric("Hallucination risk", result["hallucination_risk"])
    st.caption(f"Governance: {result['governance_status']} | Trace: {result['trace_id']} | Latency: {result['latency_ms']} ms")
    st.subheader("Citations")
    st.json(result["citations"])
    st.subheader("Retrieved Chunks")
    st.json(result["retrieved_chunks"])
