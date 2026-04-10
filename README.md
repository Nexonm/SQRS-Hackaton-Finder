# Hackathon Team Finder

## Project Purpose

Hackathon Team Finder is a simple student project for SQRS course in Innopolis University.
The main goal is to help students find teammates for hackathons.

Users can:

- create profiles
- create team posts
- filter teams and profiles
- send join requests to teams

## Local Setup

Requirements:

- Python 3.11+
- Poetry

Install dependencies:

```bash
cd backend
poetry install --no-root
```

## How To Run

Run backend API:

```bash
cd backend
poetry run uvicorn src.main:app --reload
```

After this, API docs are available at:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

Run tests:

```bash
cd backend
poetry run pytest
```

## Data Model

The backend has three main entities:

- `Profile` - student profile with handle, name, bio, contacts, role, skills, availability
- `Team` - team post with owner, title, description, required roles, required skills, size target
- `JoinRequest` - request from one profile to join one team with status

Main join request statuses:

- `pending`
- `accepted`
- `rejected`

## Create A Profile

To create a profile, send `POST /profiles/`.

Example fields:

- `handle`
- `name`
- `bio`
- `contacts`
- `availability`
- `role_id`
- `skill_ids`

After creation, the profile is available in `GET /profiles/`.

## Create A Team

To create a team, send `POST /teams/`.

Example fields:

- `owner_handle`
- `title`
- `description`
- `size_target`
- `required_role_ids`
- `required_skill_ids`

After creation, the team is available in `GET /teams/`.

## Filter

The project supports simple filters for discovery.

Profiles can be filtered by:

- `skill_ids`
- `role_id`
- `availability`

Teams can be filtered by:

- `skill_ids`
- `role_ids`
- `owner_handle`

## Join Request

Join request flow is simple:

1. A student sends `POST /join-requests/`.
2. Team owner checks `GET /join-requests/team/{team_id}`.
3. Team owner accepts or rejects request with `PATCH /join-requests/{request_id}`.

This backend stores and returns request status for this workflow.
