import streamlit as st

st.set_page_config(page_title="Enterprise Knowledge Agent", page_icon="EK", layout="wide")
st.title("Enterprise Knowledge Agent Platform")
st.caption("Upload governed knowledge, search with hybrid retrieval, and ask citation-grounded questions.")
st.page_link("pages/1_Upload_Documents.py", label="Upload Documents")
st.page_link("pages/2_Ask_Knowledge_Agent.py", label="Ask Knowledge Agent")
st.page_link("pages/3_Search_Explorer.py", label="Search Explorer")
st.page_link("pages/4_MCP_Tools.py", label="MCP Tools")
st.page_link("pages/5_Tickets.py", label="Tickets")
st.page_link("pages/6_Observability.py", label="Observability")
