from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import DocumentStatus


class DocumentCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    reviewer_email: str | None = None
    description: str | None = None


class DocumentVersionOut(BaseModel):
    id: UUID
    document_id: UUID
    version_number: int
    status: DocumentStatus
    original_filename: str | None = None
    created_by: UUID
    created_at: datetime
    reviewed_by: UUID | None = None
    review_comment: str | None = None


class DocumentOut(BaseModel):
    id: UUID
    title: str
    owner_id: UUID
    reviewer_id: UUID | None
    created_at: datetime
    updated_at: datetime
    current_version: DocumentVersionOut


class DocumentListItemOut(BaseModel):
    id: UUID
    title: str
    owner_id: UUID
    reviewer_id: UUID | None
    current_version_number: int
    current_status: DocumentStatus
    updated_at: datetime


class DocumentSubmitRequest(BaseModel):
    comment: str | None = None


class DocumentReviewRequest(BaseModel):
    decision: Literal["Approved", "Rejected"]
    comment: str | None = None


class DocumentHistoryEventOut(BaseModel):
    id: UUID
    document_version_id: UUID
    from_status: str | None
    to_status: str
    action: str
    actor_user_id: UUID
    comment: str | None
    created_at: datetime

