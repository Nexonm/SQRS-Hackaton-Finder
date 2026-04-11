import streamlit as st
from api_client import fetch_json


def render_auth_page():
    st.title("Hackathon Team Finder")
    st.header("Login")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "profile_handle" not in st.session_state:
        st.session_state.profile_handle = ""

    if st.session_state.authenticated:
        st.success(f"Logged in as @{st.session_state.profile_handle}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.profile_handle = ""
            st.rerun()
        return True

    handle = st.text_input("Enter your handle", placeholder="username")

    if st.button("Login"):
        if not handle:
            st.error("Please enter a handle")
            return False

        profile = fetch_json(f"/profiles/{handle}")
        if profile:
            st.session_state.authenticated = True
            st.session_state.profile_handle = handle
            st.success("Login successful!")
            st.rerun()
        else:
            st.info("Profile not found. You can create one after logging in.")
            st.session_state.authenticated = True
            st.session_state.profile_handle = handle
            st.rerun()

    return False
