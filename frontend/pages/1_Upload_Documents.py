import streamlit as st

from _client import post

st.title("Upload Documents")
uploaded = st.file_uploader("File", type=["pdf", "md", "txt", "py", "java", "js", "jsx", "ts", "tsx", "json", "yaml", "yml", "go", "rs", "sql", "html", "css"])
access_level = st.selectbox("Access level", ["public", "internal", "restricted"], index=1)
if st.button("Ingest", type="primary", disabled=uploaded is None):
    files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")}
    result = post("/documents/upload", files=files, data={"access_level": access_level})
    st.success(result["message"])
    st.json(result)
