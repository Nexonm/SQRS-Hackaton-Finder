from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.routers.http_helpers import no_content_or_404, require_resource
from src.routers.response_docs import (
    TEAM_CREATE_RESPONSES,
    TEAM_DELETE_RESPONSES,
    TEAM_GET_RESPONSES,
    TEAM_UPDATE_RESPONSES,
)
from src.schemas.team import TeamCreate, TeamRead, TeamUpdate
import src.services.team_service as service

router = APIRouter()


@router.post(
    "/teams/",
    response_model=TeamRead,
    status_code=201,
    summary="Create a new team posting",
    tags=["teams"],
    responses=TEAM_CREATE_RESPONSES,
)
def create_team(data: TeamCreate, db: Session = Depends(get_db)):
    return service.create_team(db, data)


@router.get(
    "/teams/",
    response_model=list[TeamRead],
    summary="List team postings with optional filters",
    tags=["teams"],
    responses={200: {"description": "Teams list"}},
)
def list_teams(
    skill_ids: list[int] | None = Query(default=None),
    role_ids: list[int] | None = Query(default=None),
    owner_handle: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return service.list_teams(
        db,
        skill_ids=skill_ids,
        role_ids=role_ids,
        owner_handle=owner_handle,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/teams/{team_id}",
    response_model=TeamRead,
    summary="Get a team posting by ID",
    tags=["teams"],
    responses=TEAM_GET_RESPONSES,
)
def get_team(team_id: int, db: Session = Depends(get_db)):
    return require_resource(
        service.get_team(db, team_id),
        f"Team {team_id} not found",
    )


@router.put(
    "/teams/{team_id}",
    response_model=TeamRead,
    summary="Update a team posting (owner only)",
    tags=["teams"],
    responses=TEAM_UPDATE_RESPONSES,
)
def update_team(
    team_id: int,
    data: TeamUpdate,
    owner_handle: str,
    db: Session = Depends(get_db),
):
    return require_resource(
        service.update_team(db, team_id, owner_handle, data),
        f"Team {team_id} not found",
    )


@router.delete(
    "/teams/{team_id}",
    status_code=204,
    summary="Delete a team posting (owner only)",
    tags=["teams"],
    responses=TEAM_DELETE_RESPONSES,
)
def delete_team(
    team_id: int,
    owner_handle: str,
    db: Session = Depends(get_db),
):
    return no_content_or_404(
        service.delete_team(db, team_id, owner_handle),
        f"Team {team_id} not found",
    )
