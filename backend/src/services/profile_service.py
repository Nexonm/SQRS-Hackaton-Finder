from sqlalchemy.orm import Session

from src.models.profile import Profile
from src.schemas.profile import ProfileCreate, ProfileUpdate


def create_profile(db: Session, data: ProfileCreate) -> Profile:
    raise NotImplementedError


def get_profile_by_handle(db: Session, handle: str) -> Profile | None:
    raise NotImplementedError


def list_profiles(db: Session, skill: str | None = None) -> list[Profile]:
    raise NotImplementedError


def update_profile(
    db: Session, handle: str, data: ProfileUpdate
) -> Profile | None:
    raise NotImplementedError
