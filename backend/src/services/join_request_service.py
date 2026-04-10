from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.join_request import JoinRequest
from src.schemas.join_request import JoinRequestCreate
from src.services.common import ensure_owner
from src.services.join_request_lookup_service import (
    get_profile_or_404,
    get_request_owner_team_or_404,
    get_team_or_404,
    raise_if_duplicate_request,
)


def create_join_request(db: Session, data: JoinRequestCreate) -> JoinRequest:
    """Create a new request from a student to a team.

    Args:
        db: Active SQLAlchemy session.
        data: Incoming join request payload from API schema.

    Returns:
        Created JoinRequest ORM object with initial pending status.
    """
    team = get_team_or_404(db, data.team_id)
    get_profile_or_404(db, data.applicant_handle)

    if team.owner_handle == data.applicant_handle:
        raise HTTPException(
            status_code=400,
            detail="Team owner cannot request to join their own team",
        )

    raise_if_duplicate_request(db, data.team_id, data.applicant_handle)

    join_request = JoinRequest(
        team_id=data.team_id,
        applicant_handle=data.applicant_handle,
        status="pending",
    )
    db.add(join_request)
    db.commit()
    db.refresh(join_request)
    return join_request


def get_join_request(db: Session, request_id: int) -> JoinRequest | None:
    """Load one join request by primary key.

    Args:
        db: Active SQLAlchemy session.
        request_id: Join request primary key used for lookup.

    Returns:
        JoinRequest object or None when nothing is found.
    """
    return db.get(JoinRequest, request_id)


def list_join_requests_for_team(
    db: Session, team_id: int, owner_handle: str
) -> list[JoinRequest]:
    """List requests for one team after owner check.

    Args:
        db: Active SQLAlchemy session.
        team_id: Team primary key used for lookup.
        owner_handle: Handle used for ownership check.

    Returns:
        List of join requests ordered by creation id.
    """
    team = get_team_or_404(db, team_id)
    ensure_owner(
        team.owner_handle,
        owner_handle,
        "Only the team owner can view join requests",
    )

    stmt = (
        select(JoinRequest)
        .where(JoinRequest.team_id == team_id)
        .order_by(JoinRequest.id.asc())
    )
    return db.scalars(stmt).all()


def update_join_request_status(
    db: Session, request_id: int, owner_handle: str, status: str
) -> JoinRequest | None:
    """Accept or reject one pending join request.

    Args:
        db: Active SQLAlchemy session.
        request_id: Join request primary key used for lookup.
        owner_handle: Handle used for ownership check.
        status: Target status, expected accepted or rejected.

    Returns:
        Updated JoinRequest object or None when request does not exist.
    """
    join_request = db.get(JoinRequest, request_id)
    if join_request is None:
        return None

    team = get_request_owner_team_or_404(db, join_request)
    ensure_owner(
        team.owner_handle,
        owner_handle,
        "Only the team owner can update join requests",
    )

    if join_request.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Join request has already been processed",
        )

    join_request.status = status
    db.add(join_request)
    db.commit()
    db.refresh(join_request)
    return join_request
