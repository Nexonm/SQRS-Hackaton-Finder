import streamlit as st
from api_client import fetch_json, post_json, put_json, delete_request


def render_my_teams_page():
    st.header("My Teams")

    if "profile_handle" not in st.session_state:
        st.error("Please login first")
        return

    handle = st.session_state.profile_handle

    owned = fetch_json(
        "/teams/",
        params={"owner_handle": handle, "limit": 100}
    )

    all_teams = fetch_json("/teams/", params={"limit": 100})
    joined = []
    if all_teams:
        for team in all_teams:
            if team["owner_handle"] == handle:
                continue
            reqs = fetch_json(
                f"/join-requests/team/{team['id']}",
                params={"owner_handle": team["owner_handle"]}
            )
            if reqs:
                for req in reqs:
                    if req["applicant_handle"] == handle:
                        if req["status"] == "accepted":
                            joined.append(team)
                            break

    teams = (owned or []) + joined

    if teams:
        for team in teams:
            with st.container():
                st.subheader(team["title"])
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

                with st.expander("Edit Team"):
                    if is_owner:
                        with st.form(f"edit_team_{team['id']}"):
                            title = st.text_input("Title", value=team["title"])
                            desc = st.text_area(
                                "Description",
                                value=team["description"] or "",
                                max_chars=1000
                            )
                            size = st.number_input(
                                "Size Target",
                                min_value=1,
                                max_value=100,
                                value=team["size_target"] or 4
                            )

                            skills = fetch_json("/skills")
                            roles = fetch_json("/roles")
                            skill_opts = {
                                s["name"]: s["id"] for s in skills
                            } if skills else {}
                            role_opts = {
                                r["name"]: r["id"] for r in roles
                            } if roles else {}

                            cur_roles = [
                                r["name"] for r in team["required_roles"]
                            ]
                            cur_skills = [
                                s["name"] for s in team["required_skills"]
                            ]

                            req_roles = st.multiselect(
                                "Required Roles",
                                list(role_opts.keys()),
                                default=cur_roles
                            )
                            req_skills = st.multiselect(
                                "Required Skills",
                                list(skill_opts.keys()),
                                default=cur_skills
                            )

                            if st.form_submit_button("Update Team"):
                                data = {
                                    "title": title,
                                    "description": (
                                        desc if desc else None
                                    ),
                                    "size_target": size,
                                    "required_role_ids": [
                                        role_opts[r] for r in req_roles
                                    ],
                                    "required_skill_ids": [
                                        skill_opts[s] for s in req_skills
                                    ],
                                }
                                url = (
                                    f"/teams/{team['id']}?"
                                    f"owner_handle={handle}"
                                )
                                result = put_json(url, data)
                                if result:
                                    st.success("Team updated!")
                                    st.rerun()

                    else:
                        st.write("You are a member of this team")

                with st.expander("Delete Team"):
                    if is_owner:
                        btn = st.button(
                            f"Delete {team['title']}",
                            key=f"delete_{team['id']}"
                        )
                        if btn:
                            url = (
                                f"/teams/{team['id']}?"
                                f"owner_handle={handle}"
                            )
                            if delete_request(url):
                                st.success("Team deleted!")
                                st.rerun()
                    else:
                        st.write("Only the owner can delete this team")

                st.divider()

    st.divider()
    st.subheader("Create New Team")

    skills = fetch_json("/skills")
    roles = fetch_json("/roles")
    skill_opts = {s["name"]: s["id"] for s in skills} if skills else {}
    role_opts = {r["name"]: r["id"] for r in roles} if roles else {}

    with st.form("create_team"):
        title = st.text_input("Team Title")
        desc = st.text_area("Description", max_chars=1000)
        size = st.number_input(
            "Size Target",
            min_value=1,
            max_value=100,
            value=4
        )
        req_roles = st.multiselect(
            "Required Roles",
            list(role_opts.keys())
        )
        req_skills = st.multiselect(
            "Required Skills",
            list(skill_opts.keys())
        )

        if st.form_submit_button("Create Team"):
            data = {
                "owner_handle": handle,
                "title": title,
                "description": desc if desc else None,
                "size_target": size,
                "required_role_ids": [
                    role_opts[r] for r in req_roles
                ],
                "required_skill_ids": [
                    skill_opts[s] for s in req_skills
                ],
            }
            result = post_json("/teams/", data)
            if result:
                st.success("Team created!")
                st.rerun()
