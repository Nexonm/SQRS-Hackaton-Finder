import streamlit as st
from api_client import fetch_json, post_json, put_json, delete_request


def render_my_profile_page():
    st.header("My Profile")

    if "profile_handle" not in st.session_state:
        st.error("Please login first")
        return

    handle = st.session_state.profile_handle
    profile = fetch_json(f"/profiles/{handle}")

    if profile:
        st.subheader("Your Profile")
        st.write(f"**Name:** {profile['name']}")
        st.write(f"**Handle:** @{profile['handle']}")
        st.write(f"**Bio:** {profile['bio'] or 'N/A'}")
        st.write(f"**Contacts:** {profile['contacts'] or 'N/A'}")
        avail = "Available" if profile["availability"] else "Busy"
        st.write(f"**Availability:** {avail}")
        st.write(f"**Role:** {profile['role']['name']}")
        sk = ", ".join(s["name"] for s in profile["skills"])
        st.write(f"**Skills:** {sk}")

        st.divider()
        st.subheader("Update Profile")

        skills = fetch_json("/skills")
        roles = fetch_json("/roles")
        skill_opts = {s["name"]: s["id"] for s in skills} if skills else {}
        role_opts = {r["name"]: r["id"] for r in roles} if roles else {}

        with st.form("update_profile"):
            name = st.text_input("Name", value=profile["name"])
            bio = st.text_area(
                "Bio", value=profile["bio"] or "", max_chars=1000
            )
            contacts = st.text_input(
                "Contacts",
                value=profile["contacts"] or ""
            )
            avail = st.checkbox(
                "Available for hackathons",
                value=profile["availability"]
            )
            role_name = profile["role"]["name"]
            role_idx = (
                list(role_opts.keys()).index(role_name)
                if role_name in role_opts
                else 0
            )
            role = st.selectbox("Role", list(role_opts.keys()), index=role_idx)
            cur_skills = [s["name"] for s in profile["skills"]]
            sel_skills = st.multiselect(
                "Skills",
                list(skill_opts.keys()),
                default=cur_skills
            )

            if st.form_submit_button("Update"):
                data = {
                    "name": name,
                    "bio": bio if bio else None,
                    "contacts": contacts if contacts else None,
                    "availability": avail,
                    "role_id": role_opts[role],
                    "skill_ids": [skill_opts[s] for s in sel_skills],
                }
                result = put_json(f"/profiles/{handle}", data)
                if result:
                    st.success("Profile updated!")
                    st.rerun()

        st.divider()
        if st.button("Delete Profile", type="secondary"):
            if delete_request(f"/profiles/{handle}"):
                st.success("Profile deleted!")
                st.session_state.authenticated = False
                st.session_state.profile_handle = ""
                st.rerun()
    else:
        st.subheader("Create New Profile")

        skills = fetch_json("/skills")
        roles = fetch_json("/roles")
        skill_opts = {s["name"]: s["id"] for s in skills} if skills else {}
        role_opts = {r["name"]: r["id"] for r in roles} if roles else {}

        with st.form("create_profile"):
            name = st.text_input("Name")
            bio = st.text_area("Bio", max_chars=1000)
            contacts = st.text_input("Contacts (Telegram, email, etc.)")
            avail = st.checkbox("Available for hackathons", value=True)
            role = st.selectbox("Role", list(role_opts.keys()))
            sel_skills = st.multiselect("Skills", list(skill_opts.keys()))

            if st.form_submit_button("Create Profile"):
                data = {
                    "handle": handle,
                    "name": name,
                    "bio": bio if bio else None,
                    "contacts": contacts if contacts else None,
                    "availability": avail,
                    "role_id": role_opts[role],
                    "skill_ids": [skill_opts[s] for s in sel_skills],
                }
                result = post_json("/profiles/", data)
                if result:
                    st.success("Profile created!")
                    st.rerun()
