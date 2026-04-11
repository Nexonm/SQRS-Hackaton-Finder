import httpx
import streamlit as st

BASE_URL = "http://localhost:8000"


def get_client() -> httpx.Client:
    return httpx.Client(base_url=BASE_URL, timeout=10.0)


def fetch_json(url: str, params: dict | None = None) -> list | dict | None:
    try:
        with get_client() as client:
            response = client.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                return None
    except httpx.RequestError as e:
        st.error(f"Connection error: {e}")
        return None


def post_json(url: str, data: dict) -> dict | None:
    try:
        with get_client() as client:
            response = client.post(url, json=data)
            if response.status_code in (200, 201):
                return response.json()
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
                return None
    except httpx.RequestError as e:
        st.error(f"Connection error: {e}")
        return None


def put_json(url: str, data: dict) -> dict | None:
    try:
        with get_client() as client:
            response = client.put(url, json=data)
            if response.status_code in (200, 201):
                return response.json()
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
                return None
    except httpx.RequestError as e:
        st.error(f"Connection error: {e}")
        return None


def patch_json(url: str, data: dict) -> dict | None:
    try:
        with get_client() as client:
            response = client.patch(url, json=data)
            if response.status_code in (200, 201):
                return response.json()
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
                return None
    except httpx.RequestError as e:
        st.error(f"Connection error: {e}")
        return None


def delete_request(url: str) -> bool:
    try:
        with get_client() as client:
            response = client.delete(url)
            if response.status_code == 204:
                return True
            else:
                st.error(f"Error: {response.status_code}")
                return False
    except httpx.RequestError as e:
        st.error(f"Connection error: {e}")
        return False
