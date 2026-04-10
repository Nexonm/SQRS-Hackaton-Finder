"""Create/update/delete operations for profiles."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.profile import Profile
from src.schemas.profile import ProfileCreate, ProfileUpdate
from src.services.common import apply_scalar_updates, utcnow_iso
from src.services.profile_dictionary_service import (
    get_role_or_422,
    get_skills_or_422,
    seed_profile_dictionaries,
)
from src.services.profile_query_service import get_profile_by_handle


def create_profile(db: Session, data: ProfileCreate) -> Profile:
    """Create one participant profile after validating dictionaries."""
    seed_profile_dictionaries(db)

    existing = db.get(Profile, data.handle)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Handle already taken")

    get_role_or_422(db, data.role_id)
    skills = get_skills_or_422(db, data.skill_ids)

    now = utcnow_iso()
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


def apply_profile_updates(
    db: Session,
    profile: Profile,
    updates: dict,
) -> None:
    """Update relation fields first, then scalar fields."""
    role_id = updates.get("role_id")
    if role_id is not None:
        profile.role_id = get_role_or_422(db, role_id).id

    if "skill_ids" in updates and updates["skill_ids"] is not None:
        profile.skills = get_skills_or_422(db, updates["skill_ids"])

    apply_scalar_updates(
        profile,
        updates,
        ("name", "bio", "contacts", "availability"),
    )


def update_profile(
    db: Session,
    handle: str,
    data: ProfileUpdate,
) -> Profile | None:
    """Apply partial updates to an existing profile."""
    profile = get_profile_by_handle(db, handle)
    if profile is None:
        return None

    updates = data.model_dump(exclude_unset=True)
    apply_profile_updates(db, profile, updates)
    profile.updated_at = utcnow_iso()
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def delete_profile(db: Session, handle: str) -> bool:
    """Delete a profile by handle and return success flag."""
    profile = db.get(Profile, handle)
    if profile is None:
        return False

    db.delete(profile)
    db.commit()
    return True
