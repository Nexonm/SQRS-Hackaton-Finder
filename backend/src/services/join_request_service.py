from sqlalchemy.orm import Session

from src.models.join_request import JoinRequest
from src.schemas.join_request import JoinRequestCreate


def create_join_request(db: Session, data: JoinRequestCreate) -> JoinRequest:
    raise NotImplementedError


def get_join_request(db: Session, request_id: int) -> JoinRequest | None:
    raise NotImplementedError


def list_join_requests_for_team(
    db: Session, team_id: int
) -> list[JoinRequest]:
    raise NotImplementedError


def update_join_request_status(
    db: Session, request_id: int, owner_handle: str, status: str
) -> JoinRequest | None:
    raise NotImplementedError
