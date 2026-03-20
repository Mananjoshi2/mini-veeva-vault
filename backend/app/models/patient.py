from __future__ import annotations

import uuid

from sqlalchemy import DateTime, ForeignKey, Text, func, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PatientRecord(Base):
    __tablename__ = "patient_records"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    treatment: Mapped[str] = mapped_column(String(255), nullable=False)
    outcome: Mapped[str] = mapped_column(Text, nullable=False)

    # Column name intentionally matches the requirement.
    timestamp: Mapped[DateTime] = mapped_column("timestamp", DateTime(timezone=True), nullable=False, default=func.now())

