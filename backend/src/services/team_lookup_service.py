"""Lookup helpers for teams and related dictionaries."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.models.profile import Profile, Role, Skill
from src.models.team import Team
from src.services.common import load_entities_or_422, require_entity


def get_profile_or_404(db: Session, handle: str) -> Profile:
    """Ensure the team owner profile exists before create/update."""
    return require_entity(db, Profile, handle, f"Profile '{handle}' not found")


def get_roles_or_422(db: Session, role_ids: list[int]) -> list[Role]:
    """Validate required role ids for a team."""
    return load_entities_or_422(db, Role, role_ids, "role_id")


def get_skills_or_422(db: Session, skill_ids: list[int]) -> list[Skill]:
    """Validate required skill ids for a team."""
    return load_entities_or_422(db, Skill, skill_ids, "skill_id")


def load_team(db: Session, team_id: int) -> Team | None:
    """Load one team with eager-loaded roles and skills."""
    stmt = (
        select(Team)
        .where(Team.id == team_id)
        .options(
            joinedload(Team.required_roles),
            joinedload(Team.required_skills),
        )
    )
    return db.scalars(stmt).unique().first()
