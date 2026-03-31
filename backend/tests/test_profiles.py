from fastapi.testclient import TestClient


def _get_seed_ids(client: TestClient) -> tuple[int, list[int]]:
    roles = client.get("/roles")
    skills = client.get("/skills")
    assert roles.status_code == 200
    assert skills.status_code == 200

    role_id = roles.json()[0]["id"]
    skill_ids = [skills.json()[0]["id"], skills.json()[1]["id"]]
    return role_id, skill_ids


def test_create_profile(client: TestClient):
    role_id, skill_ids = _get_seed_ids(client)
    payload = {
        "handle": "john_doe",
        "name": "John Doe",
        "bio": "Backend student",
        "contacts": "@john",
        "availability": True,
        "role_id": role_id,
        "skill_ids": skill_ids,
    }

    response = client.post("/profiles", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["handle"] == "john_doe"
    assert data["role"]["id"] == role_id
    assert len(data["skills"]) == 2


def test_list_profiles(client: TestClient):
    role_id, skill_ids = _get_seed_ids(client)
    client.post(
        "/profiles",
        json={
            "handle": "alice_1",
            "name": "Alice",
            "role_id": role_id,
            "skill_ids": [skill_ids[0]],
        },
    )
    client.post(
        "/profiles",
        json={
            "handle": "bob_1",
            "name": "Bob",
            "role_id": role_id,
            "skill_ids": [skill_ids[1]],
        },
    )

    response = client.get("/profiles?limit=20&offset=0")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_profile_by_handle(client: TestClient):
    role_id, _ = _get_seed_ids(client)
    client.post(
        "/profiles",
        json={
            "handle": "charlie_1",
            "name": "Charlie",
            "role_id": role_id,
            "skill_ids": [],
        },
    )

    response = client.get("/profiles/charlie_1")
    assert response.status_code == 200
    assert response.json()["handle"] == "charlie_1"


def test_update_profile(client: TestClient):
    role_id, skill_ids = _get_seed_ids(client)
    client.post(
        "/profiles",
        json={
            "handle": "diana_1",
            "name": "Diana",
            "role_id": role_id,
            "skill_ids": [skill_ids[0]],
        },
    )

    response = client.put(
        "/profiles/diana_1",
        json={
            "name": "Diana Updated",
            "availability": False,
            "skill_ids": [skill_ids[1]],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Diana Updated"
    assert data["availability"] is False
    assert [item["id"] for item in data["skills"]] == [skill_ids[1]]


def test_list_profiles_filter_by_skill(client: TestClient):
    role_id, skill_ids = _get_seed_ids(client)
    client.post(
        "/profiles",
        json={
            "handle": "eva_1",
            "name": "Eva",
            "role_id": role_id,
            "skill_ids": skill_ids,
        },
    )
    client.post(
        "/profiles",
        json={
            "handle": "frank_1",
            "name": "Frank",
            "role_id": role_id,
            "skill_ids": [skill_ids[0]],
        },
    )

    response = client.get(f"/profiles?skill_ids={skill_ids[0]}&skill_ids={skill_ids[1]}")
    assert response.status_code == 200
    assert [item["handle"] for item in response.json()] == ["eva_1"]


def test_create_profile_duplicate_handle_returns_409(client: TestClient):
    role_id, _ = _get_seed_ids(client)
    payload = {
        "handle": "taken_handle",
        "name": "First",
        "role_id": role_id,
        "skill_ids": [],
    }
    client.post("/profiles", json=payload)

    response = client.post("/profiles", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "Handle already taken"


def test_create_profile_invalid_role_returns_422(client: TestClient):
    response = client.post(
        "/profiles",
        json={
            "handle": "invalid_role",
            "name": "User",
            "role_id": 99999,
            "skill_ids": [],
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "role_id 99999 does not exist"
