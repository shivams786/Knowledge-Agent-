import json

import streamlit as st

from _client import get, post

st.title("MCP Tools")
tools = get("/tools")
names = [tool["name"] for tool in tools]
selected = st.selectbox("Tool", names)
tool = next(item for item in tools if item["name"] == selected)
st.write(tool["description"])
st.json(tool["input_schema"])
raw = st.text_area("JSON arguments", value='{"query": "governance", "top_k": 3, "filters": {"search_mode": "hybrid", "access_level": "internal"}}')
if st.button("Execute"):
    result = post(f"/tools/{selected}/execute", json={"arguments": json.loads(raw)})
    st.json(result)
