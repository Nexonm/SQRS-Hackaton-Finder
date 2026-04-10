"""Read/query operations for teams."""

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from src.models.team import Team, team_roles, team_skills
from src.services.common import build_all_match_subquery, unique_ids
from src.services.team_lookup_service import load_team


def base_team_query() -> Select[tuple[Team]]:
    """Create the common eager-loaded query for team reads."""
    return (
        select(Team)
        .options(
            joinedload(Team.required_roles),
            joinedload(Team.required_skills),
        )
        .order_by(Team.id.asc())
    )


def apply_team_filters(
    stmt: Select[tuple[Team]],
    skill_ids: list[int] | None,
    role_ids: list[int] | None,
    owner_handle: str | None,
) -> Select[tuple[Team]]:
    """Apply owner, skill, and role filters for team discovery."""
    if owner_handle is not None:
        stmt = stmt.where(Team.owner_handle == owner_handle)

    skills_subquery = build_all_match_subquery(
        team_skills,
        team_skills.c.team_id,
        team_skills.c.skill_id,
        unique_ids(skill_ids),
    )
    if skills_subquery is not None:
        stmt = stmt.where(Team.id.in_(skills_subquery))

    roles_subquery = build_all_match_subquery(
        team_roles,
        team_roles.c.team_id,
        team_roles.c.role_id,
        unique_ids(role_ids),
    )
    if roles_subquery is not None:
        stmt = stmt.where(Team.id.in_(roles_subquery))

    return stmt


def get_team(db: Session, team_id: int) -> Team | None:
    """Load one team by id for read endpoints."""
    return load_team(db, team_id)


def list_teams(
    db: Session,
    skill_ids: list[int] | None = None,
    role_ids: list[int] | None = None,
    owner_handle: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Team]:
    """List teams with optional filters and pagination."""
    stmt = apply_team_filters(
        base_team_query(),
        skill_ids,
        role_ids,
        owner_handle,
    )
    stmt = stmt.offset(offset).limit(limit)
    return db.scalars(stmt).unique().all()
