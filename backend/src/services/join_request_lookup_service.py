"""Lookup helpers for join request workflow."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.join_request import JoinRequest
from src.models.profile import Profile
from src.models.team import Team
from src.services.common import require_entity


def get_team_or_404(db: Session, team_id: int) -> Team:
    """Load a team for join request checks."""
    return require_entity(db, Team, team_id, f"Team {team_id} not found")


def get_profile_or_404(db: Session, handle: str) -> Profile:
    """Load an applicant profile for join request checks."""
    return require_entity(db, Profile, handle, f"Profile '{handle}' not found")


def get_request_owner_team_or_404(
    db: Session,
    join_request: JoinRequest,
) -> Team:
    """Resolve the team that owns a stored join request."""
    return get_team_or_404(db, join_request.team_id)


def raise_if_duplicate_request(
    db: Session,
    team_id: int,
    applicant_handle: str,
) -> None:
    """Reject duplicate pending-or-processed requests for the same pair."""
    existing = db.scalars(
        select(JoinRequest).where(
            JoinRequest.team_id == team_id,
            JoinRequest.applicant_handle == applicant_handle,
        )
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Join request already exists",
        )
