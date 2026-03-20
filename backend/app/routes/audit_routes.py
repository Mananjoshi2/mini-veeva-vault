from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user, require_roles
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogOut
from app.models.enums import UserRole


router = APIRouter(prefix="/api/audit-logs", tags=["audit-logs"])


@router.get("", response_model=list[AuditLogOut])
def api_audit_logs(
    entity_type: str | None = Query(default=None),
    action: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    user_id: str | None = Query(default=None),
    from_timestamp: datetime | None = Query(default=None),
    to_timestamp: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.ADMIN)),
):
    q = db.query(AuditLog)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))
    if entity_id:
        q = q.filter(AuditLog.entity_id == entity_id)
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    if from_timestamp:
        q = q.filter(AuditLog.timestamp >= from_timestamp)
    if to_timestamp:
        q = q.filter(AuditLog.timestamp <= to_timestamp)

    rows = q.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
    return [
        AuditLogOut(
            id=r.id,
            user_id=r.user_id,
            action=r.action,
            timestamp=r.timestamp,
            entity_type=r.entity_type,
            entity_id=r.entity_id,
            details=r.details,
        )
        for r in rows
    ]

