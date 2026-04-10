from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.join_request import (
    JoinRequestCreate,
    JoinRequestRead,
    JoinRequestStatusUpdate,
)
import src.services.join_request_service as service

router = APIRouter(prefix="/join-requests", tags=["join-requests"])


@router.post(
    "/",
    response_model=JoinRequestRead,
    status_code=201,
    summary="Submit a join request",
)
def create_join_request(
    data: JoinRequestCreate, db: Session = Depends(get_db)
):
    return service.create_join_request(db, data)


@router.get(
    "/team/{team_id}",
    response_model=list[JoinRequestRead],
    summary="List join requests for a team",
)
def list_join_requests(
    team_id: int,
    owner_handle: str,
    db: Session = Depends(get_db),
):
    return service.list_join_requests_for_team(db, team_id, owner_handle)


@router.patch(
    "/{request_id}",
    response_model=JoinRequestRead,
    summary="Accept or reject a join request",
)
def update_join_request_status(
    request_id: int,
    data: JoinRequestStatusUpdate,
    owner_handle: str,
    db: Session = Depends(get_db),
):
    join_request = service.update_join_request_status(
        db,
        request_id,
        owner_handle,
        data.status,
    )
    if join_request is None:
        raise HTTPException(
            status_code=404,
            detail=f"Join request {request_id} not found",
        )
    return join_request
