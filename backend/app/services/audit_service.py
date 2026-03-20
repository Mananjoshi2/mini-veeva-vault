from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    *,
    user_id: UUID | None,
    action: str,
    entity_type: str | None,
    entity_id: str | None,
    details: dict[str, Any] | None = None,
    timestamp: datetime | None = None,
) -> None:
    row = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(row)
    db.flush()

