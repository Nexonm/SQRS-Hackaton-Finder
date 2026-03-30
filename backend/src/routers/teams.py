from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.team import TeamCreate, TeamRead, TeamUpdate
import src.services.team_service as service

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamRead, summary="Create a new team posting")
def create_team(data: TeamCreate, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/", response_model=list[TeamRead], summary="List team postings")
def list_teams(
    skill: str | None = None,
    role: str | None = None,
    db: Session = Depends(get_db),
):
    raise NotImplementedError


@router.get("/{team_id}", response_model=TeamRead, summary="Get a team by ID")
def get_team(team_id: int, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.patch(
    "/{team_id}", response_model=TeamRead, summary="Update a team posting"
)
def update_team(
    team_id: int,
    data: TeamUpdate,
    owner_handle: str,
    db: Session = Depends(get_db),
):
    raise NotImplementedError
