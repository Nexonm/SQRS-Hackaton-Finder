from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.routers.http_helpers import no_content_or_404, require_resource
from src.routers.response_docs import (
    PROFILE_CREATE_RESPONSES,
    PROFILE_DELETE_RESPONSES,
    PROFILE_GET_RESPONSES,
    PROFILE_UPDATE_RESPONSES,
)
from src.schemas.profile import (
    ProfileCreate,
    ProfileRead,
    ProfileUpdate,
    RoleOut,
    SkillOut,
)
import src.services.profile_service as service

router = APIRouter()


@router.get(
    "/skills",
    response_model=list[SkillOut],
    summary="Get available skills",
    tags=["skills"],
    responses={200: {"description": "Skill dictionary"}},
)
def list_skills(db: Session = Depends(get_db)):
    return service.list_skills(db)


@router.get(
    "/roles",
    response_model=list[RoleOut],
    summary="Get available roles",
    tags=["roles"],
    responses={200: {"description": "Role dictionary"}},
)
def list_roles(db: Session = Depends(get_db)):
    return service.list_roles(db)


@router.post(
    "/profiles/",
    response_model=ProfileRead,
    status_code=201,
    summary="Create a new participant profile",
    tags=["profiles"],
    responses=PROFILE_CREATE_RESPONSES,
)
def create_profile(data: ProfileCreate, db: Session = Depends(get_db)):
    return service.create_profile(db, data)


@router.get(
    "/profiles/",
    response_model=list[ProfileRead],
    summary="List profiles with filters and pagination",
    tags=["profiles"],
    responses={200: {"description": "Profiles list"}},
)
def list_profiles(
    skill_ids: list[int] | None = Query(default=None),
    role_id: int | None = None,
    availability: bool | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return service.list_profiles(
        db,
        skill_ids=skill_ids,
        role_id=role_id,
        availability=availability,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/profiles/{handle}",
    response_model=ProfileRead,
    summary="Get profile by handle",
    tags=["profiles"],
    responses=PROFILE_GET_RESPONSES,
)
def get_profile(handle: str, db: Session = Depends(get_db)):
    return require_resource(
        service.get_profile_by_handle(db, handle),
        f"Profile '{handle}' not found",
    )


@router.put(
    "/profiles/{handle}",
    response_model=ProfileRead,
    summary="Update profile fields",
    tags=["profiles"],
    responses=PROFILE_UPDATE_RESPONSES,
)
def update_profile(
    handle: str, data: ProfileUpdate, db: Session = Depends(get_db)
):
    return require_resource(
        service.update_profile(db, handle, data),
        f"Profile '{handle}' not found",
    )


@router.delete(
    "/profiles/{handle}",
    status_code=204,
    summary="Delete a profile",
    tags=["profiles"],
    responses=PROFILE_DELETE_RESPONSES,
)
def delete_profile(handle: str, db: Session = Depends(get_db)):
    return no_content_or_404(
        service.delete_profile(db, handle),
        f"Profile '{handle}' not found",
    )
