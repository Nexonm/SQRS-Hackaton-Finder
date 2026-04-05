from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.team import TeamCreate, TeamRead, TeamUpdate
import src.services.team_service as service

router = APIRouter()


@router.post(
    "/teams/",
    response_model=TeamRead,
    status_code=201,
    summary="Create a new team posting",
    tags=["teams"],
    responses={
        201: {"description": "Team created"},
        404: {"description": "Owner profile not found"},
        422: {"description": "Validation error (invalid role_id or skill_id)"},
    },
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
    responses={
        200: {"description": "Team found"},
        404: {"description": "Team not found"},
    },
)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = service.get_team(db, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
    return team


@router.put(
    "/teams/{team_id}",
    response_model=TeamRead,
    summary="Update a team posting (owner only)",
    tags=["teams"],
    responses={
        200: {"description": "Team updated"},
        403: {"description": "Not the team owner"},
        404: {"description": "Team not found"},
        422: {"description": "Validation error (invalid role_id or skill_id)"},
    },
)
def update_team(
    team_id: int,
    data: TeamUpdate,
    owner_handle: str,
    db: Session = Depends(get_db),
):
    team = service.update_team(db, team_id, owner_handle, data)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
    return team


@router.delete(
    "/teams/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a team posting (owner only)",
    tags=["teams"],
    responses={
        204: {"description": "Team deleted"},
        403: {"description": "Not the team owner"},
        404: {"description": "Team not found"},
    },
)
def delete_team(
    team_id: int,
    owner_handle: str,
    db: Session = Depends(get_db),
):
    deleted = service.delete_team(db, team_id, owner_handle)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
