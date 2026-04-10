from fastapi.testclient import TestClient


def test_create_join_request(client: TestClient):
    _, applicant_handle, team_id = _create_team_with_applicant(client)

    response = client.post(
        "/join-requests/",
        json={
            "team_id": team_id,
            "applicant_handle": applicant_handle,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["team_id"] == team_id
    assert data["applicant_handle"] == applicant_handle
    assert data["status"] == "pending"
    assert isinstance(data["id"], int)


def test_list_join_requests_for_team(client: TestClient):
    (
        owner_handle,
        applicant_handle,
        team_id,
    ) = _create_team_with_applicant(client)
    client.post(
        "/join-requests/",
        json={
            "team_id": team_id,
            "applicant_handle": applicant_handle,
        },
    )

    response = client.get(
        f"/join-requests/team/{team_id}?owner_handle={owner_handle}"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["applicant_handle"] == applicant_handle
    assert data[0]["status"] == "pending"


def test_accept_join_request(client: TestClient):
    (
        owner_handle,
        applicant_handle,
        team_id,
    ) = _create_team_with_applicant(client)
    create_response = client.post(
        "/join-requests/",
        json={
            "team_id": team_id,
            "applicant_handle": applicant_handle,
        },
    )
    request_id = create_response.json()["id"]

    response = client.patch(
        f"/join-requests/{request_id}?owner_handle={owner_handle}",
        json={"status": "accepted"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == request_id
    assert data["status"] == "accepted"


def test_reject_join_request(client: TestClient):
    (
        owner_handle,
        applicant_handle,
        team_id,
    ) = _create_team_with_applicant(client)
    create_response = client.post(
        "/join-requests/",
        json={
            "team_id": team_id,
            "applicant_handle": applicant_handle,
        },
    )
    request_id = create_response.json()["id"]

    response = client.patch(
        f"/join-requests/{request_id}?owner_handle={owner_handle}",
        json={"status": "rejected"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == request_id
    assert data["status"] == "rejected"


def test_join_request_wrong_owner_returns_403(client: TestClient):
    _, applicant_handle, team_id = _create_team_with_applicant(client)
    create_response = client.post(
        "/join-requests/",
        json={
            "team_id": team_id,
            "applicant_handle": applicant_handle,
        },
    )
    request_id = create_response.json()["id"]

    response = client.patch(
        f"/join-requests/{request_id}?owner_handle=wrong_owner",
        json={"status": "accepted"},
    )

    assert response.status_code == 403


def test_duplicate_join_request_returns_409(client: TestClient):
    _, applicant_handle, team_id = _create_team_with_applicant(client)
    payload = {
        "team_id": team_id,
        "applicant_handle": applicant_handle,
    }

    first_response = client.post("/join-requests/", json=payload)
    second_response = client.post("/join-requests/", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_owner_cannot_join_own_team(client: TestClient):
    owner_handle, _, team_id = _create_team_with_applicant(client)

    response = client.post(
        "/join-requests/",
        json={
            "team_id": team_id,
            "applicant_handle": owner_handle,
        },
    )

    assert response.status_code == 400


def _create_team_with_applicant(
    client: TestClient,
) -> tuple[str, str, int]:
    roles_response = client.get("/roles")
    skills_response = client.get("/skills")
    assert roles_response.status_code == 200
    assert skills_response.status_code == 200

    role_id = roles_response.json()[0]["id"]
    skill_id = skills_response.json()[0]["id"]

    owner_handle = "join_owner"
    applicant_handle = "join_applicant"

    owner_response = client.post(
        "/profiles/",
        json={
            "handle": owner_handle,
            "name": "Owner",
            "role_id": role_id,
            "skill_ids": [],
        },
    )
    applicant_response = client.post(
        "/profiles/",
        json={
            "handle": applicant_handle,
            "name": "Applicant",
            "role_id": role_id,
            "skill_ids": [skill_id],
        },
    )
    assert owner_response.status_code == 201
    assert applicant_response.status_code == 201

    team_response = client.post(
        "/teams/",
        json={
            "owner_handle": owner_handle,
            "title": "Join Team",
            "description": "Team for join request tests",
            "size_target": 4,
            "required_role_ids": [role_id],
            "required_skill_ids": [skill_id],
        },
    )
    assert team_response.status_code == 201

    return owner_handle, applicant_handle, team_response.json()["id"]
