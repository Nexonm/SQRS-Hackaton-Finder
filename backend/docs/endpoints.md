# Backend Endpoints

## Overview

- Framework: FastAPI
- Default local base URL: `http://127.0.0.1:8000`
- Content type: JSON for request bodies and responses unless noted otherwise
- Canonical route style: most collection routes are defined with a trailing slash, such as `/profiles/` and `/teams/`

## Authentication And Authorization

- No real authentication layer is implemented in the backend.
- There are no JWTs, sessions, API keys, or OAuth flows in the codebase.
- Some owner-only operations rely on a plain `owner_handle` query parameter.
- Because `owner_handle` is not verified against an authenticated user, it should be treated as a lightweight ownership check for coursework/demo purposes, not production-grade security.

## Common Response Notes

- Validation errors are returned by FastAPI/Pydantic as `422 Unprocessable Entity`.
- Not-found cases are returned as `404 Not Found`.
- Ownership violations are returned as `403 Forbidden`.
- Deletions return `204 No Content` with an empty body.
- Role and skill dictionaries are seeded lazily when `/roles`, `/skills`, or profile creation is used.

## Endpoint Summary

| Method | Path | Purpose | Ownership/Auth |
| --- | --- | --- | --- |
| `GET` | `/skills` | List available skills | Public |
| `GET` | `/roles` | List available roles | Public |
| `POST` | `/profiles/` | Create a participant profile | Public |
| `GET` | `/profiles/` | List profiles with filters | Public |
| `GET` | `/profiles/{handle}` | Fetch one profile | Public |
| `PUT` | `/profiles/{handle}` | Update one profile | Public |
| `DELETE` | `/profiles/{handle}` | Delete one profile | Public |
| `POST` | `/teams/` | Create a team posting | Public |
| `GET` | `/teams/` | List teams with filters | Public |
| `GET` | `/teams/{team_id}` | Fetch one team | Public |
| `PUT` | `/teams/{team_id}` | Update a team posting | `owner_handle` query parameter required |
| `DELETE` | `/teams/{team_id}` | Delete a team posting | `owner_handle` query parameter required |
| `POST` | `/join-requests/` | Submit a join request | Public |
| `GET` | `/join-requests/team/{team_id}` | List join requests for a team | `owner_handle` query parameter required |
| `PATCH` | `/join-requests/{request_id}` | Accept or reject a join request | `owner_handle` query parameter required |

## Reference Data Endpoints

### `GET /skills`

Returns the seeded skill dictionary.

- Authentication: none
- Query parameters: none
- Request body: none
- Success response: `200 OK`

Example response:

```json
[
  { "id": 1, "name": "Python" },
  { "id": 2, "name": "JavaScript" }
]
```

Example usage:

```bash
curl http://127.0.0.1:8000/skills
```

### `GET /roles`

Returns the seeded role dictionary.

- Authentication: none
- Query parameters: none
- Request body: none
- Success response: `200 OK`

Example response:

```json
[
  { "id": 1, "name": "Backend Developer" },
  { "id": 2, "name": "Frontend Developer" }
]
```

Example usage:

```bash
curl http://127.0.0.1:8000/roles
```

## Profile Endpoints

### `POST /profiles/`

Creates a participant profile.

- Authentication: none
- Request body fields:
  - `handle`: string, `^[a-z0-9_-]{3,40}$`
  - `name`: string, `1..100` chars
  - `bio`: optional string, up to `1000` chars
  - `contacts`: optional string, up to `300` chars
  - `availability`: boolean, defaults to `true`
  - `role_id`: integer
  - `skill_ids`: array of integers, max `20`
- Success response: `201 Created`
- Other known responses:
  - `409` if the handle already exists
  - `422` if `role_id` or any `skill_ids` entry does not exist

Example request:

```json
{
  "handle": "john_doe",
  "name": "John Doe",
  "bio": "Backend student",
  "contacts": "@john",
  "availability": true,
  "role_id": 1,
  "skill_ids": [1, 2]
}
```

Example response:

```json
{
  "handle": "john_doe",
  "name": "John Doe",
  "bio": "Backend student",
  "contacts": "@john",
  "availability": true,
  "role": { "id": 1, "name": "Backend Developer" },
  "skills": [
    { "id": 1, "name": "Python" },
    { "id": 2, "name": "JavaScript" }
  ],
  "created_at": "2026-04-11T16:00:00+00:00",
  "updated_at": "2026-04-11T16:00:00+00:00"
}
```

Example usage:

```bash
curl -X POST http://127.0.0.1:8000/profiles/ \
  -H "Content-Type: application/json" \
  -d "{\"handle\":\"john_doe\",\"name\":\"John Doe\",\"role_id\":1,\"skill_ids\":[1,2]}"
```

### `GET /profiles/`

Lists profiles with optional filtering and pagination.

- Authentication: none
- Query parameters:
  - `skill_ids`: repeated integer parameter, AND-matched
  - `role_id`: optional integer
  - `availability`: optional boolean
  - `limit`: integer, default `20`, min `1`, max `100`
  - `offset`: integer, default `0`, min `0`
- Success response: `200 OK`

Example response:

```json
[
  {
    "handle": "john_doe",
    "name": "John Doe",
    "bio": "Backend student",
    "contacts": "@john",
    "availability": true,
    "role": { "id": 1, "name": "Backend Developer" },
    "skills": [{ "id": 1, "name": "Python" }],
    "created_at": "2026-04-11T16:00:00+00:00",
    "updated_at": "2026-04-11T16:00:00+00:00"
  }
]
```

Example usage:

```bash
curl "http://127.0.0.1:8000/profiles/?skill_ids=1&skill_ids=2&availability=true&limit=20&offset=0"
```

### `GET /profiles/{handle}`

Fetches a single profile by handle.

- Authentication: none
- Path parameters:
  - `handle`: string
- Success response: `200 OK`
- Other known responses:
  - `404` if the profile does not exist

Example usage:

```bash
curl http://127.0.0.1:8000/profiles/john_doe
```

### `PUT /profiles/{handle}`

Partially updates a profile. Every field in the request body is optional.

- Authentication: none
- Path parameters:
  - `handle`: string
- Request body fields:
  - `name`: optional string
  - `bio`: optional string
  - `contacts`: optional string
  - `availability`: optional boolean
  - `role_id`: optional integer
  - `skill_ids`: optional array of integers
- Success response: `200 OK`
- Other known responses:
  - `404` if the profile does not exist
  - `422` if any referenced role or skill id does not exist

Example request:

```json
{
  "name": "John Updated",
  "availability": false,
  "skill_ids": [2]
}
```

Example usage:

```bash
curl -X PUT "http://127.0.0.1:8000/profiles/john_doe" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"John Updated\",\"availability\":false,\"skill_ids\":[2]}"
```

### `DELETE /profiles/{handle}`

Deletes a profile.

- Authentication: none
- Path parameters:
  - `handle`: string
- Success response: `204 No Content`
- Other known responses:
  - `404` if the profile does not exist

Example usage:

```bash
curl -X DELETE http://127.0.0.1:8000/profiles/john_doe
```

## Team Endpoints

### `POST /teams/`

Creates a team posting for an existing profile.

- Authentication: none
- Request body fields:
  - `owner_handle`: string
  - `title`: string, `1..128` chars
  - `description`: optional string, up to `1000` chars
  - `size_target`: optional integer, `1..100`
  - `required_role_ids`: array of integers, max `13`
  - `required_skill_ids`: array of integers, max `20`
- Success response: `201 Created`
- Other known responses:
  - `404` if `owner_handle` does not match an existing profile
  - `422` if any required role or skill id does not exist

Example request:

```json
{
  "owner_handle": "john_doe",
  "title": "Need a frontend teammate",
  "description": "Hackathon team focused on rapid MVP delivery",
  "size_target": 4,
  "required_role_ids": [2],
  "required_skill_ids": [2, 11]
}
```

Example response:

```json
{
  "id": 1,
  "owner_handle": "john_doe",
  "title": "Need a frontend teammate",
  "description": "Hackathon team focused on rapid MVP delivery",
  "size_target": 4,
  "required_roles": [{ "id": 2, "name": "Frontend Developer" }],
  "required_skills": [
    { "id": 2, "name": "JavaScript" },
    { "id": 11, "name": "React" }
  ],
  "created_at": "2026-04-11T16:00:00+00:00",
  "updated_at": "2026-04-11T16:00:00+00:00"
}
```

Example usage:

```bash
curl -X POST http://127.0.0.1:8000/teams/ \
  -H "Content-Type: application/json" \
  -d "{\"owner_handle\":\"john_doe\",\"title\":\"Need a frontend teammate\",\"required_role_ids\":[2],\"required_skill_ids\":[2,11]}"
```

### `GET /teams/`

Lists team postings with optional filtering and pagination.

- Authentication: none
- Query parameters:
  - `skill_ids`: repeated integer parameter, AND-matched
  - `role_ids`: repeated integer parameter, AND-matched
  - `owner_handle`: optional string
  - `limit`: integer, default `20`, min `1`, max `100`
  - `offset`: integer, default `0`, min `0`
- Success response: `200 OK`

Example response:

```json
[
  {
    "id": 1,
    "owner_handle": "john_doe",
    "title": "Need a frontend teammate",
    "description": "Hackathon team focused on rapid MVP delivery",
    "size_target": 4,
    "required_roles": [{ "id": 2, "name": "Frontend Developer" }],
    "required_skills": [{ "id": 11, "name": "React" }],
    "created_at": "2026-04-11T16:00:00+00:00",
    "updated_at": "2026-04-11T16:00:00+00:00"
  }
]
```

Example usage:

```bash
curl "http://127.0.0.1:8000/teams/?role_ids=2&skill_ids=11&owner_handle=john_doe"
```

### `GET /teams/{team_id}`

Fetches one team posting by numeric ID.

- Authentication: none
- Path parameters:
  - `team_id`: integer
- Success response: `200 OK`
- Other known responses:
  - `404` if the team does not exist

Example usage:

```bash
curl http://127.0.0.1:8000/teams/1
```

### `PUT /teams/{team_id}`

Partially updates a team posting. Ownership is checked using `owner_handle` in the query string.

- Authentication: no real authentication
- Ownership requirement: `owner_handle` must match the stored team owner
- Path parameters:
  - `team_id`: integer
- Query parameters:
  - `owner_handle`: string, required
- Request body fields:
  - `title`: optional string
  - `description`: optional string
  - `size_target`: optional integer
  - `required_role_ids`: optional array of integers
  - `required_skill_ids`: optional array of integers
- Success response: `200 OK`
- Other known responses:
  - `403` if `owner_handle` does not match the owner
  - `404` if the team does not exist
  - `422` if any role or skill id does not exist

Example request:

```json
{
  "title": "Updated Team Title",
  "size_target": 6
}
```

Example usage:

```bash
curl -X PUT "http://127.0.0.1:8000/teams/1?owner_handle=john_doe" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Updated Team Title\",\"size_target\":6}"
```

### `DELETE /teams/{team_id}`

Deletes a team posting. Ownership is checked using `owner_handle` in the query string.

- Authentication: no real authentication
- Ownership requirement: `owner_handle` must match the stored team owner
- Path parameters:
  - `team_id`: integer
- Query parameters:
  - `owner_handle`: string, required
- Success response: `204 No Content`
- Other known responses:
  - `403` if `owner_handle` does not match the owner
  - `404` if the team does not exist

Example usage:

```bash
curl -X DELETE "http://127.0.0.1:8000/teams/1?owner_handle=john_doe"
```

## Join Request Endpoints

### `POST /join-requests/`

Creates a join request with initial status `pending`.

- Authentication: none
- Request body fields:
  - `team_id`: integer
  - `applicant_handle`: string
- Success response: `201 Created`
- Other known responses:
  - `400` if the applicant is the team owner
  - `404` if the team or applicant profile does not exist
  - `409` if a request for the same `(team_id, applicant_handle)` already exists

Example request:

```json
{
  "team_id": 1,
  "applicant_handle": "alice_dev"
}
```

Example response:

```json
{
  "id": 1,
  "team_id": 1,
  "applicant_handle": "alice_dev",
  "status": "pending"
}
```

Example usage:

```bash
curl -X POST http://127.0.0.1:8000/join-requests/ \
  -H "Content-Type: application/json" \
  -d "{\"team_id\":1,\"applicant_handle\":\"alice_dev\"}"
```

### `GET /join-requests/team/{team_id}`

Lists all join requests for one team in ascending request ID order.

- Authentication: no real authentication
- Ownership requirement: `owner_handle` must match the stored team owner
- Path parameters:
  - `team_id`: integer
- Query parameters:
  - `owner_handle`: string, required
- Success response: `200 OK`
- Other known responses:
  - `403` if `owner_handle` does not match the owner
  - `404` if the team does not exist

Example usage:

```bash
curl "http://127.0.0.1:8000/join-requests/team/1?owner_handle=john_doe"
```

### `PATCH /join-requests/{request_id}`

Accepts or rejects a pending join request.

- Authentication: no real authentication
- Ownership requirement: `owner_handle` must match the team owner
- Path parameters:
  - `request_id`: integer
- Query parameters:
  - `owner_handle`: string, required
- Request body fields:
  - `status`: must be either `"accepted"` or `"rejected"`
- Success response: `200 OK`
- Other known responses:
  - `403` if `owner_handle` does not match the team owner
  - `404` if the join request does not exist
  - `409` if the join request has already been processed
  - `422` if `status` is not one of the allowed literals

Example request:

```json
{
  "status": "accepted"
}
```

Example usage:

```bash
curl -X PATCH "http://127.0.0.1:8000/join-requests/1?owner_handle=john_doe" \
  -H "Content-Type: application/json" \
  -d "{\"status\":\"accepted\"}"
```
