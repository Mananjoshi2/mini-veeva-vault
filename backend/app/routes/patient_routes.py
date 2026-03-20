from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user, require_roles
from app.models.enums import UserRole
from app.schemas.patient import PatientCreateRequest, PatientOut
from app.services.patient_service import create_patient, get_patient, list_patients


router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.post("", response_model=PatientOut, status_code=201)
def api_create_patient(
    req: PatientCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.RESEARCHER, UserRole.ADMIN)),
):
    patient = create_patient(db, actor=current_user, req=req)
    return PatientOut(
        patient_id=patient.patient_id,
        treatment=patient.treatment,
        outcome=patient.outcome,
        timestamp=patient.timestamp,
    )


@router.get("", response_model=list[PatientOut])
def api_list_patients(
    treatment: str | None = Query(default=None),
    outcome: str | None = Query(default=None),
    from_timestamp: datetime | None = Query(default=None),
    to_timestamp: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    items, _total = list_patients(
        db,
        treatment=treatment,
        outcome=outcome,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp,
        limit=limit,
        offset=offset,
    )
    return [
        PatientOut(patient_id=p.patient_id, treatment=p.treatment, outcome=p.outcome, timestamp=p.timestamp)
        for p in items
    ]


@router.get("/{patient_id}", response_model=PatientOut)
def api_get_patient(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    patient = get_patient(db, patient_id)
    return PatientOut(
        patient_id=patient.patient_id,
        treatment=patient.treatment,
        outcome=patient.outcome,
        timestamp=patient.timestamp,
    )

