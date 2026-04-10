"""Tiny pure helpers shared by service modules."""

from datetime import datetime, timezone
from typing import Any


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def unique_ids(ids: list[int] | None) -> list[int]:
    return list(dict.fromkeys(ids or []))


def apply_scalar_updates(
    entity: Any,
    updates: dict[str, Any],
    fields: tuple[str, ...],
) -> None:
    for field in fields:
        if field in updates:
            setattr(entity, field, updates[field])
