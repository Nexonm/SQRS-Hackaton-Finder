from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from src.models.profile import Profile, Role, Skill
from src.models.team import Team, team_roles, team_skills
from src.schemas.team import TeamCreate, TeamUpdate


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_profile_or_404(db: Session, handle: str) -> Profile:
    profile = db.get(Profile, handle)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail=f"Profile '{handle}' not found",
        )
    return profile


def _get_roles_or_422(db: Session, role_ids: list[int]) -> list[Role]:
    unique_ids = list(dict.fromkeys(role_ids))
    if not unique_ids:
        return []
    roles = db.scalars(select(Role).where(Role.id.in_(unique_ids))).all()
    roles_by_id = {role.id: role for role in roles}
    for role_id in unique_ids:
        if role_id not in roles_by_id:
            raise HTTPException(
                status_code=422,
                detail=f"role_id {role_id} does not exist",
            )
    return [roles_by_id[rid] for rid in unique_ids]


def _get_skills_or_422(db: Session, skill_ids: list[int]) -> list[Skill]:
    unique_ids = list(dict.fromkeys(skill_ids))
    if not unique_ids:
        return []
    skills = db.scalars(select(Skill).where(Skill.id.in_(unique_ids))).all()
    skills_by_id = {skill.id: skill for skill in skills}
    for skill_id in unique_ids:
        if skill_id not in skills_by_id:
            raise HTTPException(
                status_code=422,
                detail=f"skill_id {skill_id} does not exist",
            )
    return [skills_by_id[sid] for sid in unique_ids]


def _load_team(db: Session, team_id: int) -> Team | None:
    stmt = (
        select(Team)
        .where(Team.id == team_id)
        .options(
            joinedload(Team.required_roles),
            joinedload(Team.required_skills),
        )
    )
    return db.scalars(stmt).unique().first()


def create_team(db: Session, data: TeamCreate) -> Team:
    _get_profile_or_404(db, data.owner_handle)
    roles = _get_roles_or_422(db, data.required_role_ids)
    skills = _get_skills_or_422(db, data.required_skill_ids)

    now = _utcnow_iso()
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
    return _load_team(db, team.id)


def get_team(db: Session, team_id: int) -> Team | None:
    return _load_team(db, team_id)


def list_teams(
    db: Session,
    skill_ids: list[int] | None = None,
    role_ids: list[int] | None = None,
    owner_handle: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Team]:
    stmt: Select[tuple[Team]] = (
        select(Team)
        .options(
            joinedload(Team.required_roles),
            joinedload(Team.required_skills),
        )
        .order_by(Team.id.asc())
    )

    if owner_handle is not None:
        stmt = stmt.where(Team.owner_handle == owner_handle)

    unique_skill_ids = list(dict.fromkeys(skill_ids or []))
    if unique_skill_ids:
        skills_subquery = (
            select(team_skills.c.team_id)
            .where(team_skills.c.skill_id.in_(unique_skill_ids))
            .group_by(team_skills.c.team_id)
            .having(
                func.count(func.distinct(team_skills.c.skill_id))
                == len(unique_skill_ids)
            )
        )
        stmt = stmt.where(Team.id.in_(skills_subquery))

    unique_role_ids = list(dict.fromkeys(role_ids or []))
    if unique_role_ids:
        roles_subquery = (
            select(team_roles.c.team_id)
            .where(team_roles.c.role_id.in_(unique_role_ids))
            .group_by(team_roles.c.team_id)
            .having(
                func.count(func.distinct(team_roles.c.role_id))
                == len(unique_role_ids)
            )
        )
        stmt = stmt.where(Team.id.in_(roles_subquery))

    stmt = stmt.offset(offset).limit(limit)
    return db.scalars(stmt).unique().all()


def update_team(
    db: Session, team_id: int, owner_handle: str, data: TeamUpdate
) -> Team | None:
    team = _load_team(db, team_id)
    if team is None:
        return None

    if team.owner_handle != owner_handle:
        raise HTTPException(
            status_code=403,
            detail="Only the team owner can update this team",
        )

    updates = data.model_dump(exclude_unset=True)

    if "required_role_ids" in updates and updates["required_role_ids"] is not None:
        team.required_roles = _get_roles_or_422(db, updates["required_role_ids"])

    if "required_skill_ids" in updates and updates["required_skill_ids"] is not None:
        team.required_skills = _get_skills_or_422(db, updates["required_skill_ids"])

    for field in ("title", "description", "size_target"):
        if field in updates:
            setattr(team, field, updates[field])

    team.updated_at = _utcnow_iso()
    db.add(team)
    db.commit()
    return _load_team(db, team_id)


def delete_team(db: Session, team_id: int, owner_handle: str) -> bool:
    team = db.get(Team, team_id)
    if team is None:
        return False

    if team.owner_handle != owner_handle:
        raise HTTPException(
            status_code=403,
            detail="Only the team owner can delete this team",
        )

    db.delete(team)
    db.commit()
    return True
