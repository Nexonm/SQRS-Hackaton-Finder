"""Database helpers for validation and common query pieces."""

from typing import Any

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.services.base_utils import unique_ids


def require_entity(
    db: Session,
    model: Any,
    key: Any,
    detail: str,
):
    """Load one entity by primary key or raise 404.

    Args:
        db: Active SQLAlchemy session.
        model: ORM model class used for lookup.
        key: Primary key value.
        detail: Error message for 404 response.

    Returns:
        Loaded ORM object.
    """
    entity = db.get(model, key)
    if entity is None:
        raise HTTPException(status_code=404, detail=detail)
    return entity


def load_entities_or_422(
    db: Session,
    model: Any,
    ids: list[int] | None,
    field_name: str,
) -> list[Any]:
    """Load many entities by ids and keep input order.

    Args:
        db: Active SQLAlchemy session.
        model: ORM model class with integer id field.
        ids: Input ids from API payload.
        field_name: Field name used in validation error text.

    Returns:
        List of ORM objects in the same order as input ids.
    """
    normalized_ids = unique_ids(ids)
    if not normalized_ids:
        return []

    entities = db.scalars(
        select(model).where(model.id.in_(normalized_ids))
    ).all()
    entities_by_id = {entity.id: entity for entity in entities}

    for entity_id in normalized_ids:
        if entity_id not in entities_by_id:
            raise HTTPException(
                status_code=422,
                detail=f"{field_name} {entity_id} does not exist",
            )

    return [entities_by_id[entity_id] for entity_id in normalized_ids]


def build_all_match_subquery(
    link_table: Any,
    parent_column: Any,
    child_column: Any,
    ids: list[int] | None,
):
    """Build an AND-style filter for many-to-many lookups.

    Args:
        link_table: Association table used in many-to-many relation.
        parent_column: Parent id column from the association table.
        child_column: Child id column from the association table.
        ids: Optional list of required child ids.

    Returns:
        SQLAlchemy subquery or None when no ids are passed.
    """
    normalized_ids = unique_ids(ids)
    if not normalized_ids:
        return None

    return (
        select(parent_column)
        .where(child_column.in_(normalized_ids))
        .group_by(parent_column)
        .having(func.count(func.distinct(child_column)) == len(normalized_ids))
    )


def ensure_owner(
    actual_owner: str,
    requested_owner: str,
    message: str,
) -> None:
    """Raise 403 when a user is not allowed to mutate a resource.

    Args:
        actual_owner: Owner stored in the database.
        requested_owner: Owner handle provided in request.
        message: Error text for forbidden access.

    Returns:
        None. The function raises on mismatch.
    """
    if actual_owner != requested_owner:
        raise HTTPException(status_code=403, detail=message)
