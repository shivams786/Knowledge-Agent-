import streamlit as st

from _client import get

st.title("Search Explorer")
query = st.text_input("Search query")
mode = st.selectbox("Search mode", ["hybrid", "semantic", "keyword"])
top_k = st.slider("Top K", 1, 30, 10)
if st.button("Search", disabled=not query.strip()):
    result = get("/search", q=query, top_k=top_k, search_mode=mode, access_level="internal")
    for item in result["results"]:
        st.markdown(f"**{item['source_filename']}** `{item['citation_id']}`")
        st.caption(f"hybrid={item['hybrid_score']} semantic={item['similarity_score']} keyword={item['keyword_score']}")
        st.write(item["chunk_text"][:1000])
