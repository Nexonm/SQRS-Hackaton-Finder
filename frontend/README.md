# Hackathon Team Finder — Streamlit Frontend

## Overview

Streamlit-based frontend for the Hackathon Team Finder application. Provides a simple UI for:
- Creating and managing user profiles
- Browsing and creating team postings
- Sending and managing join requests

## Prerequisites

- Python 3.11+
- Poetry (dependency management)
- Running backend API at `http://localhost:8000`

## Installation

```bash
cd frontend
poetry install
```

## Running the Application

1. Start the backend server first:
```bash
cd ../backend
poetry run uvicorn src.main:app --reload
```

2. In a separate terminal, start the frontend:
```bash
cd frontend
poetry run streamlit run src/app.py
```

3. Open the URL shown in terminal

## Features

### Profiles
- View all profiles with filtering by skills, roles, and availability
- Create new profile with handle, name, bio, skills, and role
- Update existing profile
- Delete profile

### Teams
- Browse all team postings
- Filter teams by required skills and roles
- Create new team posting
- Edit and delete your own teams

### Join Requests
- Send join requests to teams
- Accept or reject requests for your teams
- Track request status (pending, accepted, rejected)

## Architecture

The frontend follows a modular page-based structure:

```
src/
├── app.py              # Main application entry point
├── api_client.py       # API helper functions
└── pages/
    ├── auth.py         # Login/authentication page
    ├── profiles_page.py    # Browse all profiles
    ├── teams_page.py       # Browse all teams
    ├── my_profile.py       # User profile management
    ├── my_teams.py         # User team management
    └── join_requests.py    # Join request management
```

## API Communication

All API calls go through helper functions in `api_client.py`:
- `fetch_json()` — GET requests
- `post_json()` — POST requests
- `put_json()` — PUT requests
- `delete_request()` — DELETE requests

Base URL: `http://localhost:8000`

## Authentication

The app uses simple handle-based authentication:
1. Enter your handle on the login page
2. If profile exists, you're logged in
3. If not, you can create a profile
4. Session state maintains authentication across pages
