"""Facade module kept for router imports."""

from src.services.team_mutation_service import (
    create_team,
    delete_team,
    update_team,
)
from src.services.team_query_service import get_team, list_teams

__all__ = [
    "create_team",
    "delete_team",
    "get_team",
    "list_teams",
    "update_team",
]
