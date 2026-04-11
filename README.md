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

Install git hooks for local quality checks:

```bash
cd backend
poetry run pre-commit install
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

Run pre-commit checks manually:

```bash
cd backend
poetry run pre-commit run --all-files
```

## Backend Documentation

- [Endpoints](backend/docs/endpoints.md)
- [Testing suite](backend/docs/testing-suite.md)
- [General backend architecture](backend/docs/backend-architecture.md)

Run the performance check for read endpoints:

```bash
cd backend
poetry run locust -f locustfile.py --headless -H http://127.0.0.1:8000 -u 10 -r 2 -t 1m --only-summary --csv performance/locust
poetry run python scripts/check_locust_p95.py performance/locust_stats.csv --max-p95 200
```

The Locust scenario exercises the read-heavy discovery endpoints:

- `GET /roles`
- `GET /skills`
- `GET /profiles/`
- `GET /teams/`
- filtered reads on `GET /profiles/` and `GET /teams/`

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
