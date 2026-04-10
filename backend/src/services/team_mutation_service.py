"""Create/update/delete operations for teams."""

from sqlalchemy.orm import Session

from src.models.team import Team
from src.schemas.team import TeamCreate, TeamUpdate
from src.services.common import apply_scalar_updates, ensure_owner, utcnow_iso
from src.services.team_lookup_service import (
    get_profile_or_404,
    get_roles_or_422,
    get_skills_or_422,
    load_team,
)


def apply_team_updates(
    db: Session,
    team: Team,
    updates: dict,
) -> None:
    """Update team relations first, then simple scalar fields.

    Args:
        db: Active SQLAlchemy session.
        team: Existing team ORM object to mutate.
        updates: Partial update dictionary from schema payload.

    Returns:
        None. The function mutates the passed team instance in place.
    """
    role_ids = updates.get("required_role_ids")
    if role_ids is not None:
        team.required_roles = get_roles_or_422(db, role_ids)

    skill_ids = updates.get("required_skill_ids")
    if skill_ids is not None:
        team.required_skills = get_skills_or_422(db, skill_ids)

    apply_scalar_updates(
        team,
        updates,
        ("title", "description", "size_target"),
    )


def create_team(db: Session, data: TeamCreate) -> Team:
    """Create one team posting owned by an existing profile.

    Args:
        db: Active SQLAlchemy session.
        data: Incoming team payload from API schema.

    Returns:
        Created Team ORM object with required roles and skills loaded.
    """
    get_profile_or_404(db, data.owner_handle)
    roles = get_roles_or_422(db, data.required_role_ids)
    skills = get_skills_or_422(db, data.required_skill_ids)

    now = utcnow_iso()
    team = Team(
        owner_handle=data.owner_handle,
        title=data.title,
        description=data.description,
        size_target=data.size_target,
        created_at=now,
        updated_at=now,
    )
    team.required_roles = roles
    team.required_skills = skills

    db.add(team)
    db.commit()
    db.refresh(team)
    return load_team(db, team.id)


def update_team(
    db: Session,
    team_id: int,
    owner_handle: str,
    data: TeamUpdate,
) -> Team | None:
    """Apply partial updates to a team owned by the caller.

    Args:
        db: Active SQLAlchemy session.
        team_id: Team primary key used for lookup.
        owner_handle: Handle used for ownership check.
        data: Partial update payload from API schema.

    Returns:
        Updated Team object or None when team does not exist.
    """
    team = load_team(db, team_id)
    if team is None:
        return None

    ensure_owner(
        team.owner_handle,
        owner_handle,
        "Only the team owner can update this team",
    )

    updates = data.model_dump(exclude_unset=True)
    apply_team_updates(db, team, updates)
    team.updated_at = utcnow_iso()
    db.add(team)
    db.commit()
    return load_team(db, team_id)


def delete_team(db: Session, team_id: int, owner_handle: str) -> bool:
    """Delete a team when the owner matches the request.

    Args:
        db: Active SQLAlchemy session.
        team_id: Team primary key used for delete.
        owner_handle: Handle used for ownership check.

    Returns:
        True when team was deleted, otherwise False.
    """
    team = db.get(Team, team_id)
    if team is None:
        return False

    ensure_owner(
        team.owner_handle,
        owner_handle,
        "Only the team owner can delete this team",
    )

    db.delete(team)
    db.commit()
    return True
