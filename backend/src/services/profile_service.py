from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from src.models.profile import Profile, Role, Skill, profile_skills
from src.schemas.profile import ProfileCreate, ProfileUpdate


SKILL_SEED = [
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "Kotlin",
    "Go",
    "Rust",
    "C++",
    "C#",
    "SQL",
    "React",
    "Vue",
    "FastAPI",
    "Django",
    "Spring Boot",
    "Docker",
    "Kubernetes",
    "Machine Learning",
    "Data Analysis",
    "UI/UX Design",
    "Figma",
    "PostgreSQL",
    "MongoDB",
    "Redis",
    "Git",
]

ROLE_SEED = [
    "Backend Developer",
    "Frontend Developer",
    "Fullstack Developer",
    "Mobile Developer",
    "ML Engineer",
    "Data Scientist",
    "DevOps Engineer",
    "QA Engineer",
    "UI/UX Designer",
    "Project Manager",
    "Team Lead",
    "Security Engineer",
    "Data Engineer",
]


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _seed_dictionaries(db: Session) -> None:
    if db.scalar(select(func.count(Skill.id))) == 0:
        db.add_all([Skill(name=name) for name in SKILL_SEED])
    if db.scalar(select(func.count(Role.id))) == 0:
        db.add_all([Role(name=name) for name in ROLE_SEED])
    db.commit()


def _get_role_or_422(db: Session, role_id: int) -> Role:
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(
            status_code=422, detail=f"role_id {role_id} does not exist"
        )
    return role


def _get_skills_or_422(db: Session, skill_ids: list[int]) -> list[Skill]:
    unique_ids = list(dict.fromkeys(skill_ids))
    if not unique_ids:
        return []

    skills = db.scalars(select(Skill).where(Skill.id.in_(unique_ids))).all()
    skills_by_id = {skill.id: skill for skill in skills}

    for skill_id in unique_ids:
        if skill_id not in skills_by_id:
            raise HTTPException(
                status_code=422, detail=f"skill_id {skill_id} does not exist"
            )

    return [skills_by_id[skill_id] for skill_id in unique_ids]


def list_skills(db: Session) -> list[Skill]:
    _seed_dictionaries(db)
    return db.scalars(select(Skill).order_by(Skill.id)).all()


def list_roles(db: Session) -> list[Role]:
    _seed_dictionaries(db)
    return db.scalars(select(Role).order_by(Role.id)).all()


def create_profile(db: Session, data: ProfileCreate) -> Profile:
    _seed_dictionaries(db)

    existing = db.get(Profile, data.handle)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Handle already taken")

    _get_role_or_422(db, data.role_id)
    skills = _get_skills_or_422(db, data.skill_ids)

    now = _utcnow_iso()
    profile = Profile(
        handle=data.handle,
        name=data.name,
        bio=data.bio,
        contacts=data.contacts,
        availability=data.availability,
        role_id=data.role_id,
        created_at=now,
        updated_at=now,
    )
    profile.skills = skills

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_profile_by_handle(db: Session, handle: str) -> Profile | None:
    stmt = (
        select(Profile)
        .where(Profile.handle == handle)
        .options(joinedload(Profile.role), joinedload(Profile.skills))
    )
    return db.scalars(stmt).first()


def list_profiles(
    db: Session,
    skill_ids: list[int] | None = None,
    role_id: int | None = None,
    availability: bool | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Profile]:
    stmt: Select[tuple[Profile]] = (
        select(Profile)
        .options(joinedload(Profile.role), joinedload(Profile.skills))
        .order_by(Profile.handle.asc())
    )

    if role_id is not None:
        stmt = stmt.where(Profile.role_id == role_id)

    if availability is not None:
        stmt = stmt.where(Profile.availability == availability)

    unique_skill_ids = list(dict.fromkeys(skill_ids or []))
    if unique_skill_ids:
        skills_subquery = (
            select(profile_skills.c.profile_handle)
            .where(profile_skills.c.skill_id.in_(unique_skill_ids))
            .group_by(profile_skills.c.profile_handle)
            .having(
                func.count(func.distinct(profile_skills.c.skill_id))
                == len(unique_skill_ids)
            )
        )
        stmt = stmt.where(Profile.handle.in_(skills_subquery))

    stmt = stmt.offset(offset).limit(limit)
    return db.scalars(stmt).unique().all()


def update_profile(db: Session, handle: str, data: ProfileUpdate) -> Profile | None:
    profile = get_profile_by_handle(db, handle)
    if profile is None:
        return None

    updates = data.model_dump(exclude_unset=True)

    if "role_id" in updates and updates["role_id"] is not None:
        _get_role_or_422(db, updates["role_id"])
        profile.role_id = updates["role_id"]

    if "skill_ids" in updates and updates["skill_ids"] is not None:
        profile.skills = _get_skills_or_422(db, updates["skill_ids"])

    for field_name in ("name", "bio", "contacts", "availability"):
        if field_name in updates:
            setattr(profile, field_name, updates[field_name])

    profile.updated_at = _utcnow_iso()
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def delete_profile(db: Session, handle: str) -> bool:
    profile = db.get(Profile, handle)
    if profile is None:
        return False

    db.delete(profile)
    db.commit()
    return True
