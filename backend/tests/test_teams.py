from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed_ids(client: TestClient) -> tuple[str, list[int], list[int]]:
    """Return (owner_handle, [role_id, ...], [skill_id, ...]) from seeds."""
    roles = client.get("/roles")
    skills = client.get("/skills")
    assert roles.status_code == 200
    assert skills.status_code == 200

    role_ids = [roles.json()[0]["id"], roles.json()[1]["id"]]
    skill_ids = [skills.json()[0]["id"], skills.json()[1]["id"]]

    owner_handle = "team_owner_1"
    resp = client.post(
        "/profiles/",
        json={
            "handle": owner_handle,
            "name": "Team Owner",
            "role_id": role_ids[0],
            "skill_ids": [],
        },
    )
    assert resp.status_code == 201
    return owner_handle, role_ids, skill_ids


def _create_team(
    client: TestClient,
    owner_handle: str,
    role_ids: list[int],
    skill_ids: list[int],
    title: str = "Test Team",
) -> dict:
    resp = client.post(
        "/teams/",
        json={
            "owner_handle": owner_handle,
            "title": title,
            "description": "A test team",
            "size_target": 4,
            "required_role_ids": role_ids,
            "required_skill_ids": skill_ids,
        },
    )
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_create_team(client: TestClient):
    owner, role_ids, skill_ids = _seed_ids(client)
    data = _create_team(client, owner, role_ids, skill_ids)

    assert data["owner_handle"] == owner
    assert data["title"] == "Test Team"
    assert data["size_target"] == 4
    assert [r["id"] for r in data["required_roles"]] == role_ids
    assert sorted(s["id"] for s in data["required_skills"]) == sorted(skill_ids)
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_team_unknown_owner_returns_404(client: TestClient):
    roles = client.get("/roles")
    resp = client.post(
        "/teams/",
        json={
            "owner_handle": "ghost_handle",
            "title": "Ghost Team",
            "required_role_ids": [roles.json()[0]["id"]],
            "required_skill_ids": [],
        },
    )
    assert resp.status_code == 404
    assert "ghost_handle" in resp.json()["detail"]


def test_create_team_invalid_role_returns_422(client: TestClient):
    client.get("/roles")  # seed
    owner = "owner_422"
    roles = client.get("/roles")
    client.post(
        "/profiles/",
        json={"handle": owner, "name": "Owner", "role_id": roles.json()[0]["id"], "skill_ids": []},
    )
    resp = client.post(
        "/teams/",
        json={
            "owner_handle": owner,
            "title": "Bad Team",
            "required_role_ids": [99999],
            "required_skill_ids": [],
        },
    )
    assert resp.status_code == 422
    assert "99999" in resp.json()["detail"]


def test_list_teams(client: TestClient):
    owner, role_ids, skill_ids = _seed_ids(client)
    _create_team(client, owner, role_ids[:1], skill_ids[:1], title="Team A")
    _create_team(client, owner, role_ids[1:], skill_ids[1:], title="Team B")

    resp = client.get("/teams/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_team_by_id(client: TestClient):
    owner, role_ids, skill_ids = _seed_ids(client)
    created = _create_team(client, owner, role_ids, skill_ids)

    resp = client.get(f"/teams/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]
    assert resp.json()["title"] == "Test Team"


def test_get_team_not_found_returns_404(client: TestClient):
    resp = client.get("/teams/99999")
    assert resp.status_code == 404


def test_list_teams_filter_by_skill(client: TestClient):
    owner, role_ids, skill_ids = _seed_ids(client)
    _create_team(client, owner, role_ids, skill_ids, title="Both Skills")

    owner2 = "owner_skill_2"
    roles = client.get("/roles")
    client.post(
        "/profiles/",
        json={"handle": owner2, "name": "Owner 2", "role_id": roles.json()[0]["id"], "skill_ids": []},
    )
    client.post(
        "/teams/",
        json={
            "owner_handle": owner2,
            "title": "One Skill Only",
            "required_role_ids": [],
            "required_skill_ids": [skill_ids[0]],
        },
    )

    # AND filter — only "Both Skills" has both skill_ids
    resp = client.get(f"/teams/?skill_ids={skill_ids[0]}&skill_ids={skill_ids[1]}")
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()]
    assert "Both Skills" in titles
    assert "One Skill Only" not in titles


def test_list_teams_filter_by_role(client: TestClient):
    owner, role_ids, skill_ids = _seed_ids(client)
    _create_team(client, owner, role_ids, skill_ids, title="Both Roles")

    owner2 = "owner_role_2"
    roles = client.get("/roles")
    client.post(
        "/profiles/",
        json={"handle": owner2, "name": "Owner 2", "role_id": roles.json()[0]["id"], "skill_ids": []},
    )
    client.post(
        "/teams/",
        json={
            "owner_handle": owner2,
            "title": "One Role Only",
            "required_role_ids": [role_ids[0]],
            "required_skill_ids": [],
        },
    )

    # AND filter — only "Both Roles" has both role_ids
    resp = client.get(f"/teams/?role_ids={role_ids[0]}&role_ids={role_ids[1]}")
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()]
    assert "Both Roles" in titles
    assert "One Role Only" not in titles


def test_update_team(client: TestClient):
    owner, role_ids, skill_ids = _seed_ids(client)
    created = _create_team(client, owner, role_ids, skill_ids)

    resp = client.put(
        f"/teams/{created['id']}?owner_handle={owner}",
        json={"title": "Updated Title", "size_target": 6},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated Title"
    assert data["size_target"] == 6


def test_update_team_wrong_owner_returns_403(client: TestClient):
    owner, role_ids, skill_ids = _seed_ids(client)
    created = _create_team(client, owner, role_ids, skill_ids)

    resp = client.put(
        f"/teams/{created['id']}?owner_handle=wrong_owner",
        json={"title": "Hijacked"},
    )
    assert resp.status_code == 403


def test_update_team_not_found_returns_404(client: TestClient):
    client.get("/roles")  # seed
    resp = client.put(
        "/teams/99999?owner_handle=anyone",
        json={"title": "Ghost"},
    )
    assert resp.status_code == 404


def test_delete_team(client: TestClient):
    owner, role_ids, skill_ids = _seed_ids(client)
    created = _create_team(client, owner, role_ids, skill_ids)

    resp = client.delete(f"/teams/{created['id']}?owner_handle={owner}")
    assert resp.status_code == 204

    resp = client.get(f"/teams/{created['id']}")
    assert resp.status_code == 404


def test_delete_team_wrong_owner_returns_403(client: TestClient):
    owner, role_ids, skill_ids = _seed_ids(client)
    created = _create_team(client, owner, role_ids, skill_ids)

    resp = client.delete(f"/teams/{created['id']}?owner_handle=not_the_owner")
    assert resp.status_code == 403


def test_list_teams_filter_by_owner(client: TestClient):
    owner, role_ids, skill_ids = _seed_ids(client)
    _create_team(client, owner, role_ids, skill_ids, title="Owner's Team")

    owner2 = "owner_filter_2"
    roles = client.get("/roles")
    client.post(
        "/profiles/",
        json={"handle": owner2, "name": "Owner 2", "role_id": roles.json()[0]["id"], "skill_ids": []},
    )
    client.post(
        "/teams/",
        json={
            "owner_handle": owner2,
            "title": "Other Team",
            "required_role_ids": [],
            "required_skill_ids": [],
        },
    )

    resp = client.get(f"/teams/?owner_handle={owner}")
    assert resp.status_code == 200
    assert all(t["owner_handle"] == owner for t in resp.json())
    assert len(resp.json()) == 1
