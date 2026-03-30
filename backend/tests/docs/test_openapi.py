"""R9 — OpenAPI completeness gate.

Verifies that every route registered in the FastAPI app appears in the
generated OpenAPI schema and that each operation has both a tag and a
non-empty summary.
"""
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

EXPECTED_PATHS = [
    "/profiles/",
    "/profiles/{handle}",
    "/teams/",
    "/teams/{team_id}",
    "/join-requests/",
    "/join-requests/team/{team_id}",
    "/join-requests/{request_id}",
]


def test_all_expected_paths_present():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema.get("paths", {})
    for path in EXPECTED_PATHS:
        assert path in paths, f"Missing path in OpenAPI schema: {path}"


def test_every_operation_has_tag_and_summary():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    for path, methods in schema.get("paths", {}).items():
        for method, operation in methods.items():
            assert operation.get("tags"), (
                f"{method.upper()} {path} is missing a tag"
            )
            assert operation.get("summary"), (
                f"{method.upper()} {path} is missing a summary"
            )
