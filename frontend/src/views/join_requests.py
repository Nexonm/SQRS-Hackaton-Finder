import streamlit as st
from api_client import fetch_json, post_json, patch_json


def render_join_requests_page():
    st.header("Join Requests")

    if "profile_handle" not in st.session_state:
        st.error("Please login first")
        return

    handle = st.session_state.profile_handle
    tab1, tab2 = st.tabs(["Send Request", "Manage Requests"])

    with tab1:
        st.subheader("Request to Join a Team")
        teams = fetch_json("/teams/", params={"limit": 100})
        if teams:
            other_teams = [
                t for t in teams
                if t["owner_handle"] != handle
            ]
            if other_teams:
                team_opts = {
                    f"{t['title']} (@{t['owner_handle']})": t["id"]
                    for t in other_teams
                }
                selected = st.selectbox(
                    "Select Team",
                    list(team_opts.keys())
                )

                if st.button("Send Join Request"):
                    data = {
                        "team_id": team_opts[selected],
                        "applicant_handle": handle,
                    }
                    result = post_json("/join-requests/", data)
                    if result:
                        st.success("Join request sent!")
                        st.rerun()
            else:
                st.info("No other teams available")

    with tab2:
        st.subheader("Requests for Your Teams")
        teams = fetch_json(
            "/teams/",
            params={"owner_handle": handle, "limit": 100}
        )
        if teams:
            has_requests = False
            for team in teams:
                reqs = fetch_json(
                    f"/join-requests/team/{team['id']}",
                    params={"owner_handle": handle}
                )
                if reqs:
                    pending = [r for r in reqs if r["status"] == "pending"]
                    if pending:
                        has_requests = True
                        st.write(f"**{team['title']}**")
                        for req in pending:
                            cols = st.columns([3, 1, 1])
                            with cols[0]:
                                st.write(f"@{req['applicant_handle']}")
                            with cols[1]:
                                if st.button("Accept", key=f"acc_{req['id']}"):
                                    data = {"status": "accepted"}
                                    patch_json(
                                        f"/join-requests/{req['id']}?"
                                        f"owner_handle={handle}",
                                        data,
                                    )
                                    st.rerun()
                            with cols[2]:
                                if st.button("Reject", key=f"rej_{req['id']}"):
                                    data = {"status": "rejected"}
                                    patch_json(
                                        f"/join-requests/{req['id']}?"
                                        f"owner_handle={handle}",
                                        data,
                                    )
                                    st.rerun()
                        st.divider()

            if not has_requests:
                st.info("No pending join requests")
