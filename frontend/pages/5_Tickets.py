import streamlit as st

from _client import get, patch, post

st.title("Tickets")
with st.form("create_ticket"):
    title = st.text_input("Title")
    description = st.text_area("Description")
    severity = st.selectbox("Severity", ["low", "medium", "high", "critical"], index=1)
    tags = st.text_input("Tags comma-separated")
    if st.form_submit_button("Create"):
        st.json(post("/tickets", json={"title": title, "description": description, "severity": severity, "tags": [tag.strip() for tag in tags.split(",") if tag.strip()]}))

st.subheader("Existing")
for ticket in get("/tickets"):
    with st.expander(f"#{ticket['id']} {ticket['title']} [{ticket['status']}]"):
        st.write(ticket["description"])
        new_status = st.selectbox("Status", ["open", "in_progress", "resolved", "closed"], key=ticket["id"], index=["open", "in_progress", "resolved", "closed"].index(ticket["status"]))
        if st.button("Update", key=f"update-{ticket['id']}"):
            st.json(patch(f"/tickets/{ticket['id']}", json={"status": new_status}))
