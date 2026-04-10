"""Facade module kept for router imports."""

from src.services.profile_dictionary_service import list_roles, list_skills
from src.services.profile_mutation_service import (
    create_profile,
    delete_profile,
    update_profile,
)
from src.services.profile_query_service import (
    get_profile_by_handle,
    list_profiles,
)

__all__ = [
    "create_profile",
    "delete_profile",
    "get_profile_by_handle",
    "list_profiles",
    "list_roles",
    "list_skills",
    "update_profile",
]
