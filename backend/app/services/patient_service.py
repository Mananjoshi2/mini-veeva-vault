from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.patient import PatientRecord
from app.models.user import User
from app.schemas.patient import PatientCreateRequest
from app.services.audit_service import log_action


def create_patient(db: Session, *, actor: User, req: PatientCreateRequest) -> PatientRecord:
    patient = PatientRecord(
        treatment=req.treatment,
        outcome=req.outcome,
        timestamp=req.timestamp,
    )
    db.add(patient)
    db.flush()
    db.refresh(patient)

    log_action(
        db,
        user_id=actor.id,
        action="PATIENT_CREATED",
        entity_type="PATIENT",
        entity_id=str(patient.patient_id),
        details={"treatment": patient.treatment, "outcome": patient.outcome},
    )
    db.commit()
    return patient


def list_patients(
    db: Session,
    treatment: str | None = None,
    outcome: str | None = None,
    from_timestamp: datetime | None = None,
    to_timestamp: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[PatientRecord], int]:
    limit = min(max(limit, 1), 500)

    q = db.query(PatientRecord)

    if treatment:
        q = q.filter(PatientRecord.treatment.ilike(f"%{treatment}%"))
    if outcome:
        q = q.filter(PatientRecord.outcome.ilike(f"%{outcome}%"))
    if from_timestamp:
        q = q.filter(PatientRecord.timestamp >= from_timestamp)
    if to_timestamp:
        q = q.filter(PatientRecord.timestamp <= to_timestamp)

    total = q.count()
    items = q.order_by(PatientRecord.timestamp.desc()).offset(offset).limit(limit).all()
    return items, total


def get_patient(db: Session, patient_id: UUID) -> PatientRecord:
    patient = db.query(PatientRecord).filter(PatientRecord.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient

