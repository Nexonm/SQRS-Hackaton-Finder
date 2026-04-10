from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.join_request import JoinRequest
from src.models.profile import Profile
from src.models.team import Team
from src.schemas.join_request import JoinRequestCreate


def create_join_request(db: Session, data: JoinRequestCreate) -> JoinRequest:
    team = db.get(Team, data.team_id)
    if team is None:
        raise HTTPException(
            status_code=404,
            detail=f"Team {data.team_id} not found",
        )

    applicant = db.get(Profile, data.applicant_handle)
    if applicant is None:
        raise HTTPException(
            status_code=404,
            detail=f"Profile '{data.applicant_handle}' not found",
        )

    if team.owner_handle == data.applicant_handle:
        raise HTTPException(
            status_code=400,
            detail="Team owner cannot request to join their own team",
        )

    existing = db.scalars(
        select(JoinRequest).where(
            JoinRequest.team_id == data.team_id,
            JoinRequest.applicant_handle == data.applicant_handle,
        )
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Join request already exists",
        )

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
    return db.get(JoinRequest, request_id)


def list_join_requests_for_team(
    db: Session, team_id: int, owner_handle: str
) -> list[JoinRequest]:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(
            status_code=404,
            detail=f"Team {team_id} not found",
        )

    if team.owner_handle != owner_handle:
        raise HTTPException(
            status_code=403,
            detail="Only the team owner can view join requests",
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
    join_request = db.get(JoinRequest, request_id)
    if join_request is None:
        return None

    team = db.get(Team, join_request.team_id)
    if team is None:
        raise HTTPException(
            status_code=404,
            detail=f"Team {join_request.team_id} not found",
        )

    if team.owner_handle != owner_handle:
        raise HTTPException(
            status_code=403,
            detail="Only the team owner can update join requests",
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
