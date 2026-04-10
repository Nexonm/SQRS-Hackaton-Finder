"""Read/query operations for profiles."""

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from src.models.profile import Profile, profile_skills
from src.services.common import build_all_match_subquery


def base_profile_query() -> Select[tuple[Profile]]:
    """Create the common eager-loaded query for profile reads."""
    return (
        select(Profile)
        .options(joinedload(Profile.role), joinedload(Profile.skills))
        .order_by(Profile.handle.asc())
    )


def apply_profile_filters(
    stmt: Select[tuple[Profile]],
    role_id: int | None,
    availability: bool | None,
    skill_ids: list[int] | None,
) -> Select[tuple[Profile]]:
    """Apply deterministic filters used by profile discovery."""
    if role_id is not None:
        stmt = stmt.where(Profile.role_id == role_id)

    if availability is not None:
        stmt = stmt.where(Profile.availability == availability)

    skills_subquery = build_all_match_subquery(
        profile_skills,
        profile_skills.c.profile_handle,
        profile_skills.c.skill_id,
        skill_ids,
    )
    if skills_subquery is not None:
        stmt = stmt.where(Profile.handle.in_(skills_subquery))

    return stmt


def get_profile_by_handle(db: Session, handle: str) -> Profile | None:
    """Load one profile with role and skills."""
    stmt = base_profile_query().where(Profile.handle == handle)
    return db.scalars(stmt).first()


def list_profiles(
    db: Session,
    skill_ids: list[int] | None = None,
    role_id: int | None = None,
    availability: bool | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Profile]:
    """List profiles with optional role, availability, and skill filters."""
    stmt = apply_profile_filters(
        base_profile_query(),
        role_id,
        availability,
        skill_ids,
    )
    stmt = stmt.offset(offset).limit(limit)
    return db.scalars(stmt).unique().all()
