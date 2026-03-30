from fastapi import APIRouter, Depends
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
    "/", response_model=JoinRequestRead, summary="Submit a join request"
)
def create_join_request(
    data: JoinRequestCreate, db: Session = Depends(get_db)
):
    raise NotImplementedError


@router.get(
    "/team/{team_id}",
    response_model=list[JoinRequestRead],
    summary="List join requests for a team",
)
def list_join_requests(team_id: int, db: Session = Depends(get_db)):
    raise NotImplementedError


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
    raise NotImplementedError
