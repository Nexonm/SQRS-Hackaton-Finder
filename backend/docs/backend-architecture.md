# Backend Architecture

## High-Level Summary

The backend is a small monolithic FastAPI application organized around thin routers, Pydantic schemas, SQLAlchemy ORM models, and service modules that hold most business rules. It uses SQLite as the persistence layer and creates tables automatically on startup.

## Technology Stack

- API framework: FastAPI
- Validation and serialization: Pydantic v2
- ORM and persistence: SQLAlchemy 2.x
- Database: SQLite (`hackathon_finder.db`)
- Test stack: pytest, TestClient, pytest-cov
- Dependency management: Poetry

## Directory Structure

```text
backend/
├── docs/
├── src/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   └── services/
├── tests/
├── scripts/
├── locustfile.py
└── pyproject.toml
```

## Main Layers

### 1. Application Bootstrap

Files:

- `backend/src/main.py`
- `backend/src/database.py`

Responsibilities:

- create the SQLAlchemy engine and session factory
- define the declarative base class
- create all tables with `Base.metadata.create_all(bind=engine)`
- construct the FastAPI app
- register the `profiles`, `teams`, and `join_requests` routers

Important implication:

- The application does not use Alembic or another migration tool. Schema creation is done directly from ORM metadata at runtime.

### 2. Routers

Files:

- `backend/src/routers/profiles.py`
- `backend/src/routers/teams.py`
- `backend/src/routers/join_requests.py`
- `backend/src/routers/http_helpers.py`
- `backend/src/routers/response_docs.py`

Responsibilities:

- define HTTP paths, methods, summaries, tags, and response models
- parse query parameters and request bodies
- inject the database session via `Depends(get_db)`
- delegate work to services
- translate `None` results into consistent `404`/`204` router responses through helper functions

Design characteristic:

- Routers are intentionally thin. Most domain logic lives in `src/services`.

### 3. Schemas

Files:

- `backend/src/schemas/profile.py`
- `backend/src/schemas/team.py`
- `backend/src/schemas/join_request.py`

Responsibilities:

- define input contracts such as `ProfileCreate`, `TeamCreate`, and `JoinRequestStatusUpdate`
- define output contracts such as `ProfileRead`, `TeamRead`, and `JoinRequestRead`
- enforce field length, numeric bounds, and literal constraints
- map ORM instances to response JSON with `model_config = {"from_attributes": True}`

Design characteristic:

- The code cleanly separates write schemas from read schemas, which keeps request validation and response shape explicit.

### 4. Models

Files:

- `backend/src/models/profile.py`
- `backend/src/models/team.py`
- `backend/src/models/join_request.py`

Responsibilities:

- define the persisted entities and association tables
- model the many-to-many relationships for:
  - profile to skills
  - team to required skills
  - team to required roles
- store timestamps as ISO-formatted strings

Core entities:

- `Profile`
- `Skill`
- `Role`
- `Team`
- `JoinRequest`

Notable model choices:

- `Profile.handle` is the primary key for profiles.
- `Team.owner_handle` references `Profile.handle`.
- `JoinRequest` stores `team_id`, `applicant_handle`, and a string `status`.
- `JoinRequest.status` is not backed by a database enum; the allowed transition input is enforced in the schema/service layer.

### 5. Services

Files:

- facade modules:
  - `backend/src/services/profile_service.py`
  - `backend/src/services/team_service.py`
- profile-focused modules:
  - `backend/src/services/profile_query_service.py`
  - `backend/src/services/profile_mutation_service.py`
  - `backend/src/services/profile_dictionary_service.py`
- team-focused modules:
  - `backend/src/services/team_query_service.py`
  - `backend/src/services/team_mutation_service.py`
  - `backend/src/services/team_lookup_service.py`
- join-request modules:
  - `backend/src/services/join_request_service.py`
  - `backend/src/services/join_request_lookup_service.py`
- shared helpers:
  - `backend/src/services/common.py`
  - `backend/src/services/base_utils.py`
  - `backend/src/services/db_utils.py`
  - `backend/src/services/seed_data.py`

Responsibilities:

- business rules
- ownership checks
- validation of referenced roles, skills, profiles, and teams
- composition of SQLAlchemy queries
- timestamp updates
- lazy seeding of static dictionaries

Design characteristic:

- The backend does not implement a separate repository layer. Instead, service modules combine business logic with query construction and DB lookups.

## Request Data Flow

Typical flow for a request:

1. FastAPI receives the request and matches a router function.
2. FastAPI validates path params, query params, and request JSON using the schema definitions.
3. The router gets a DB session from `get_db`.
4. The router calls a service function.
5. The service may call lookup/helper utilities for ownership checks, seed loading, validation, or reusable query fragments.
6. SQLAlchemy reads or writes ORM entities.
7. The router returns ORM objects, and FastAPI serializes them through the response model.

Example: update team flow

1. `PUT /teams/{team_id}` enters `backend/src/routers/teams.py`.
2. The router passes `team_id`, `owner_handle`, and `TeamUpdate` to `update_team(...)`.
3. `team_mutation_service.update_team(...)` loads the team, verifies ownership with `ensure_owner(...)`, applies relation/scalar changes, updates `updated_at`, commits, and reloads the team.
4. The router returns the updated `TeamRead` payload.

## Major Domain Rules

### Profiles

- handles must be unique
- role IDs and skill IDs must exist
- updates are partial and only mutate provided fields

### Teams

- a team can only be created for an existing profile owner
- required role IDs and skill IDs must exist
- update and delete actions require the request's `owner_handle` to match the stored owner

### Join Requests

- applicant profile must exist
- target team must exist
- team owners cannot request to join their own teams
- duplicate requests for the same applicant/team pair are rejected
- only the team owner can view or change requests for that team
- only `pending` requests can transition to `accepted` or `rejected`

## Design Patterns And Conventions

### Thin Controller Pattern

Routers behave like thin controllers:

- transport concerns stay in router modules
- business rules move to service modules

### Query/Mutation Split

Profiles and teams separate read logic from write logic:

- query services handle filtering and eager loading
- mutation services handle creation, updates, deletes, and rule enforcement

This improves readability and keeps large service files from becoming monolithic.

### Facade Service Modules

`profile_service.py` and `team_service.py` act as stable import facades for routers. Internally they re-export the more specialized query/mutation modules.

### Shared Helper Utilities

The backend centralizes reusable behaviors in small helpers:

- `ensure_owner(...)` for ownership checks
- `require_entity(...)` for `404` lookups
- `load_entities_or_422(...)` for foreign-key-style validation
- `build_all_match_subquery(...)` for AND-style many-to-many filtering
- `apply_scalar_updates(...)` for partial updates

### Lazy Dictionary Seeding

Skills and roles are not inserted through migrations or startup hooks. Instead, the backend seeds them when certain profile dictionary/profile operations are used.

Implication:

- reference data initialization is simple for demos
- seeding behavior is implicit, not centrally orchestrated

## Persistence Model

### Primary Relationships

- one `Profile` has one `Role`
- one `Profile` has many `Skill` values through `profile_skills`
- one `Team` belongs to one profile owner
- one `Team` has many required `Role` values through `team_roles`
- one `Team` has many required `Skill` values through `team_skills`
- one `JoinRequest` connects an applicant profile to a team

### Filtering Strategy

Profile and team list endpoints support AND-style filtering over many-to-many tables:

- profile filtering requires all requested `skill_ids` to be present
- team filtering requires all requested `skill_ids`
- team filtering also requires all requested `role_ids`

This is implemented through grouped SQL subqueries in `build_all_match_subquery(...)`.

## Strengths

- clean separation between transport, validation, and business logic
- small focused modules that are easy to navigate
- reusable helpers reduce repeated validation code
- tests exercise the application through its public HTTP interface

## Inferred Architectural Style

The backend is best described as a layered monolith with service-oriented organization:

- presentation layer: FastAPI routers
- application/business layer: service modules
- persistence layer: SQLAlchemy models plus session access