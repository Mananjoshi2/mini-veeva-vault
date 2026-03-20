from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    user_id: UUID | None
    action: str
    timestamp: datetime
    entity_type: str | None
    entity_id: str | None
    details: dict[str, Any] | None = None

