import streamlit as st
from api_client import fetch_json


def render_profiles_page():
    st.header("All Profiles")

    skills = fetch_json("/skills")
    roles = fetch_json("/roles")

    skill_opts = {s["name"]: s["id"] for s in skills} if skills else {}
    role_opts = {r["name"]: r["id"] for r in roles} if roles else {}

    col1, col2, col3 = st.columns(3)
    with col1:
        sel_skills = st.multiselect("Skills", list(skill_opts.keys()))
    with col2:
        sel_role = st.selectbox("Role", ["All"] + list(role_opts.keys()))
    with col3:
        avail = st.selectbox("Availability", ["All", "Available", "Busy"])

    if st.button("Search"):
        params = {"limit": 100}
        if sel_skills:
            params["skill_ids"] = [skill_opts[s] for s in sel_skills]
        if sel_role != "All":
            params["role_id"] = role_opts[sel_role]
        if avail != "All":
            params["availability"] = avail == "Available"

        profiles = fetch_json("/profiles/", params=params)
        if profiles:
            for p in profiles:
                with st.container():
                    st.subheader(p["name"])
                    st.write(f"**Handle:** @{p['handle']}")
                    st.write(f"**Role:** {p['role']['name']}")
                    sk = ", ".join(s["name"] for s in p["skills"])
                    st.write(f"**Skills:** {sk}")
                    st.write(f"**Bio:** {p['bio'] or 'N/A'}")
                    avail_str = "Available" if p["availability"] else "Busy"
                    st.write(f"**Availability:** {avail_str}")
                    st.write(f"**Contacts:** {p['contacts'] or 'N/A'}")
                    st.divider()
