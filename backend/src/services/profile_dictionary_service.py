"""Dictionary and validation helpers for profiles."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.profile import Role, Skill
from src.services.common import load_entities_or_422
from src.services.seed_data import ROLE_SEED, SKILL_SEED


def seed_profile_dictionaries(db: Session) -> None:
    """Populate role and skill dictionaries once for a fresh database."""
    if db.scalar(select(func.count(Skill.id))) == 0:
        db.add_all([Skill(name=name) for name in SKILL_SEED])

    if db.scalar(select(func.count(Role.id))) == 0:
        db.add_all([Role(name=name) for name in ROLE_SEED])

    db.commit()


def get_role_or_422(db: Session, role_id: int) -> Role:
    """Validate one role id and return the ORM object."""
    return load_entities_or_422(db, Role, [role_id], "role_id")[0]


def get_skills_or_422(
    db: Session,
    skill_ids: list[int] | None,
) -> list[Skill]:
    """Validate many skill ids and keep their original order."""
    return load_entities_or_422(db, Skill, skill_ids, "skill_id")


def list_skills(db: Session) -> list[Skill]:
    """Return seeded skills ordered by id for the UI."""
    seed_profile_dictionaries(db)
    return db.scalars(select(Skill).order_by(Skill.id)).all()


def list_roles(db: Session) -> list[Role]:
    """Return seeded roles ordered by id for the UI."""
    seed_profile_dictionaries(db)
    return db.scalars(select(Role).order_by(Role.id)).all()
