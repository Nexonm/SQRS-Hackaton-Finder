import streamlit as st
from views.auth import render_auth_page
from views.profiles_page import render_profiles_page
from views.teams_page import render_teams_page
from views.my_profile import render_my_profile_page
from views.my_teams import render_my_teams_page
from views.join_requests import render_join_requests_page

st.set_page_config(
    page_title="Hackathon Team Finder",
    page_icon=":mag:",
    layout="wide",
)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "profile_handle" not in st.session_state:
    st.session_state.profile_handle = ""

if not st.session_state.authenticated:
    render_auth_page()
    st.stop()

st.sidebar.write(f"Logged in as @{st.session_state.profile_handle}")
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.session_state.profile_handle = ""
    st.rerun()

page = st.sidebar.radio(
    "Menu",
    ["Profiles", "Teams", "My Profile", "My Teams", "Join Requests"],
)

if page == "Profiles":
    render_profiles_page()
elif page == "Teams":
    render_teams_page()
elif page == "My Profile":
    render_my_profile_page()
elif page == "My Teams":
    render_my_teams_page()
elif page == "Join Requests":
    render_join_requests_page()
