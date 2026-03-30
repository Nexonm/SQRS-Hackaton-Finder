from sqlalchemy.orm import Session

from src.models.team import Team
from src.schemas.team import TeamCreate, TeamUpdate


def create_team(db: Session, data: TeamCreate) -> Team:
    raise NotImplementedError


def get_team(db: Session, team_id: int) -> Team | None:
    raise NotImplementedError


def list_teams(
    db: Session,
    skill: str | None = None,
    role: str | None = None,
) -> list[Team]:
    raise NotImplementedError


def update_team(
    db: Session, team_id: int, owner_handle: str, data: TeamUpdate
) -> Team | None:
    raise NotImplementedError
