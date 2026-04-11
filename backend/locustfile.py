from __future__ import annotations

from locust import HttpUser, between, task


class HackathonReadUser(HttpUser):
    """Read-only load profile for the main discovery endpoints."""

    wait_time = between(1, 3)

    def on_start(self) -> None:
        self.skill_ids: list[int] = []
        self.role_ids: list[int] = []
        self._load_seed_dictionaries()

    def _load_seed_dictionaries(self) -> None:
        roles_response = self.client.get("/roles", name="GET /roles")
        if roles_response.ok:
            self.role_ids = [item["id"] for item in roles_response.json()]

        skills_response = self.client.get("/skills", name="GET /skills")
        if skills_response.ok:
            self.skill_ids = [item["id"] for item in skills_response.json()]

    @task(3)
    def list_profiles(self) -> None:
        self.client.get("/profiles/?limit=20&offset=0", name="GET /profiles/")

    @task(3)
    def list_teams(self) -> None:
        self.client.get("/teams/?limit=20&offset=0", name="GET /teams/")

    @task(2)
    def list_skills(self) -> None:
        self.client.get("/skills", name="GET /skills")

    @task(2)
    def list_roles(self) -> None:
        self.client.get("/roles", name="GET /roles")

    @task(2)
    def filter_profiles_by_skill(self) -> None:
        if not self.skill_ids:
            self._load_seed_dictionaries()
            if not self.skill_ids:
                return

        skill_id = self.skill_ids[0]
        self.client.get(
            f"/profiles/?skill_ids={skill_id}&limit=20&offset=0",
            name="GET /profiles/?skill_ids",
        )

    @task(2)
    def filter_teams_by_skill(self) -> None:
        if not self.skill_ids:
            self._load_seed_dictionaries()
            if not self.skill_ids:
                return

        skill_id = self.skill_ids[0]
        self.client.get(
            f"/teams/?skill_ids={skill_id}&limit=20&offset=0",
            name="GET /teams/?skill_ids",
        )
