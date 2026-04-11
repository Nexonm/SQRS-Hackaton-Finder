import streamlit as st
from api_client import fetch_json, post_json


def render_teams_page():
    st.header("All Teams")

    if "profile_handle" not in st.session_state:
        st.error("Please login first")
        return

    handle = st.session_state.profile_handle

    my_teams = fetch_json(
        "/teams/",
        params={"owner_handle": handle, "limit": 100}
    )
    my_ids = [t["id"] for t in my_teams] if my_teams else []

    skills = fetch_json("/skills")
    roles = fetch_json("/roles")

    skill_opts = {s["name"]: s["id"] for s in skills} if skills else {}
    role_opts = {r["name"]: r["id"] for r in roles} if roles else {}

    col1, col2 = st.columns(2)
    with col1:
        sel_skills = st.multiselect(
            "Required Skills",
            list(skill_opts.keys())
        )
    with col2:
        sel_roles = st.multiselect(
            "Required Roles",
            list(role_opts.keys())
        )

    if st.button("Search Teams"):
        params = {"limit": 100}
        if sel_skills:
            params["skill_ids"] = [skill_opts[s] for s in sel_skills]
        if sel_roles:
            params["role_ids"] = [role_opts[r] for r in sel_roles]

        teams = fetch_json("/teams/", params=params)
        if teams:
            for team in teams:
                with st.container():
                    st.subheader(team["title"])
                    st.write(f"**Owner:** @{team['owner_handle']}")
                    desc = team["description"] or "N/A"
                    st.write(f"**Description:** {desc}")

                    roles_str = ", ".join(
                        r["name"] for r in team["required_roles"]
                    ) or "Any"
                    st.write(f"**Required Roles:** {roles_str}")

                    skills_str = ", ".join(
                        s["name"] for s in team["required_skills"]
                    ) or "Any"
                    st.write(f"**Required Skills:** {skills_str}")

                    size = team["size_target"] or "Flexible"
                    st.write(f"**Size Target:** {size}")

                    is_owner = team["owner_handle"] == handle

                    if is_owner:
                        st.info("This is your team")
                    elif team["id"] in my_ids:
                        st.success("You are a member of this team")
                    else:
                        join_status = None
                        reqs = fetch_json(
                            f"/join-requests/team/{team['id']}",
                            params={"owner_handle": team["owner_handle"]}
                        )
                        if reqs:
                            for req in reqs:
                                if req["applicant_handle"] == handle:
                                    join_status = req["status"]
                                    break

                        if join_status == "accepted":
                            st.success("You have been accepted to this team!")
                        elif join_status == "rejected":
                            st.error("Your request was rejected")
                        elif join_status == "pending":
                            msg = "Join request sent - waiting for response"
                            st.warning(msg)
                        else:
                            btn = st.button(
                                "Request to Join",
                                key=f"join_{team['id']}"
                            )
                            if btn:
                                data = {
                                    "team_id": team["id"],
                                    "applicant_handle": handle,
                                }
                                result = post_json("/join-requests/", data)
                                if result:
                                    st.success("Join request sent!")
                                    st.rerun()

                    st.divider()
