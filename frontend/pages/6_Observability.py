import streamlit as st

from _client import get

st.title("Observability")
metrics = get("/metrics/basic")
cols = st.columns(4)
for idx, (key, value) in enumerate(metrics.items()):
    cols[idx % 4].metric(key.replace("_", " ").title(), value)
st.subheader("Recent Audit Logs")
st.json(get("/audit-logs", limit=25))
st.subheader("Health")
st.json(get("/health"))
