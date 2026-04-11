# Backend Testing Suite

## Overview

The backend test suite is API-focused. It exercises the FastAPI application through `fastapi.testclient.TestClient`, uses `pytest` as the test runner, and swaps the normal SQLite database dependency for an isolated test database.

## Tools And Frameworks

- Test runner: `pytest`
- HTTP/API testing: `fastapi.testclient.TestClient`
- Coverage reporting: `pytest-cov`
- Database for tests: SQLite via SQLAlchemy, using `test.db`
- CI environment: GitHub Actions in `.github/workflows/main.yml`

The Python dependencies that support the suite are declared in `backend/pyproject.toml`.

## Test Structure

### `backend/tests/conftest.py`

Shared fixtures for the full suite:

- Creates a dedicated SQLite test engine using `sqlite:///./test.db`
- Creates all tables before each test and drops them afterward
- Overrides FastAPI's `get_db` dependency
- Exposes a reusable `client` fixture backed by `TestClient`

### `backend/tests/test_profiles.py`

Covers the profile workflow:

- profile creation
- listing profiles
- fetching a profile by handle
- updating profile fields
- filtering by multiple skills
- duplicate handle rejection
- invalid `role_id` rejection

### `backend/tests/test_teams.py`

Covers the team workflow:

- team creation
- unknown owner rejection
- invalid role rejection
- list and get endpoints
- filtering by skills
- filtering by roles
- filtering by owner
- update success and forbidden-owner failure
- delete success and forbidden-owner failure
- team not found cases for `GET` and `PUT`

### `backend/tests/test_join_requests.py`

Covers the join-request workflow:

- join request creation
- listing requests for a team
- accepting a request
- rejecting a request
- wrong-owner rejection for updates
- duplicate request rejection
- prevention of owner joining their own team

### `backend/tests/docs/test_openapi.py`

Documentation-oriented API tests:

- verifies expected OpenAPI paths exist
- verifies each OpenAPI operation has a tag
- verifies each OpenAPI operation has a summary

### `backend/tests/docs/test_readme.py`

Documentation completeness test:

- verifies the root `README.md` exists
- verifies key project sections are present

## Coverage Status

The current suite gives meaningful coverage for:

- happy-path CRUD flows for `profiles`, `teams`, and `join-requests`
- major ownership checks on team updates/deletes and join-request updates
- some important validation failures such as duplicate profile handles, invalid role IDs, duplicate join requests, and self-join prevention
- OpenAPI presence/metadata checks
- README presence/section checks

Measured on a local run from the repository state analyzed for this document:

- total collected tests: `32`
- reported line coverage: `95%`

## Coverage Enforcement

The working local coverage command is:

```bash
cd backend
poetry run pytest --cov=src --cov-report=term-missing tests
```

Implications:

- There is a configured minimum line-coverage threshold of `75%`.
- The repository does not contain a checked-in HTML or Markdown coverage report.
- Based on the checked-in tests, coverage is strongest around router-visible behavior and core service rules, not around every edge case.
- The GitHub Actions workflow currently appears to use `-cov` instead of `--cov`, which failed when reproduced locally. The intent is clearly coverage enforcement, but the checked-in command likely needs correction in CI.

## How To Run Tests

Run the full backend suite:

```bash
cd backend
poetry run pytest
```

Run the main API tests only:

```bash
cd backend
poetry run pytest tests/*.py
```

Run tests with coverage output:

```bash
cd backend
poetry run pytest --cov=src --cov-report=term-missing tests
```

Run the OpenAPI documentation gate:

```bash
cd backend
poetry run pytest tests/docs/test_openapi.py
```

Run the README documentation gate:

```bash
cd backend
poetry run pytest tests/docs/test_readme.py
```

## CI Quality Gates

The GitHub Actions workflow runs more than just tests. For the backend it also checks:

- cyclomatic complexity via `radon`
- maintainability index via `radon`
- style via `flake8`
- security scanning via `bandit`
- documentation checks for OpenAPI and `README.md`

## Missing Critical Tests

The suite is solid for the main demo flows, but some important gaps remain.

### Endpoint Gaps

- No direct assertions for the payload shape of `GET /roles` and `GET /skills`; those endpoints are used as helpers in tests, but not validated as first-class API contracts.
- No profile deletion tests for `DELETE /profiles/{handle}` success or `404` behavior.
- No explicit not-found tests for profile `GET` and profile `PUT`.
- No tests for profile list filters by `role_id`, `availability`, `limit`, or `offset`.
- No tests for invalid `skill_ids` on profile create/update.
- No tests for join-request creation when the team does not exist.
- No tests for join-request creation when the applicant profile does not exist.
- No tests for listing team join requests with the wrong owner or unknown team.
- No tests for updating a join request that does not exist.
- No tests for re-processing an already accepted/rejected join request, even though the service returns `409`.

### Documentation Gate Gaps

- `tests/docs/test_openapi.py` does not list `/roles` or `/skills` in `EXPECTED_PATHS`, so those public endpoints are not protected by the current OpenAPI completeness gate.
- The README test checks only for section presence, not link correctness or backend-doc freshness.

## Inferred Test Philosophy

From the current suite, the backend favors:

- black-box API tests over lower-level unit tests
- fixture-based DB isolation
- coverage of the main student/demo workflows first
- targeted checks for a few critical failure paths rather than exhaustive edge-case coverage

## Unknowns

- No performance or load test results are committed, even though the README documents a Locust-based performance check.
- No contract-testing, property-based testing, or mutation-testing setup is present in the backend directory.
