from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PatientCreateRequest(BaseModel):
    treatment: str = Field(min_length=1, max_length=255)
    outcome: str = Field(min_length=1)
    timestamp: datetime | None = None


class PatientOut(BaseModel):
    patient_id: UUID
    treatment: str
    outcome: str
    timestamp: datetime

