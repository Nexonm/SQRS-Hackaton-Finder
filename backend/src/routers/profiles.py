from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate
import src.services.profile_service as service

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/", response_model=ProfileRead, summary="Create a new profile")
def create_profile(data: ProfileCreate, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/", response_model=list[ProfileRead], summary="List profiles")
def list_profiles(skill: str | None = None, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get(
    "/{handle}", response_model=ProfileRead, summary="Get profile by handle"
)
def get_profile(handle: str, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.patch(
    "/{handle}", response_model=ProfileRead, summary="Update a profile"
)
def update_profile(
    handle: str, data: ProfileUpdate, db: Session = Depends(get_db)
):
    raise NotImplementedError
