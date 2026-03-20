from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_history import DocumentHistory
from app.models.document_version import DocumentVersion
from app.models.enums import DocumentStatus, UserRole
from app.services.audit_service import log_action
from app.models.user import User


@dataclass(frozen=True)
class FileMeta:
    original_filename: str | None
    file_mime_type: str | None
    file_size_bytes: int | None


def get_latest_version(db: Session, document_id: UUID) -> DocumentVersion | None:
    return (
        db.query(DocumentVersion)
        .filter(DocumentVersion.document_id == document_id)
        .order_by(desc(DocumentVersion.version_number))
        .first()
    )


def create_document(
    db: Session,
    *,
    owner: User,
    reviewer: User | None,
    title: str,
    description: str | None,
    file_meta: FileMeta,
) -> Document:
    document = Document(
        title=title,
        owner_id=owner.id,
        reviewer_id=reviewer.id if reviewer else None,
        description=description,
    )
    db.add(document)
    db.flush()

    version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        status=DocumentStatus.DRAFT.value,
        original_filename=file_meta.original_filename,
        file_mime_type=file_meta.file_mime_type,
        file_size_bytes=file_meta.file_size_bytes,
        created_by=owner.id,
        reviewed_by=None,
        review_comment=None,
    )
    db.add(version)
    db.flush()

    history = DocumentHistory(
        document_version_id=version.id,
        from_status=None,
        to_status=DocumentStatus.DRAFT.value,
        action="NEW_VERSION",
        actor_user_id=owner.id,
        comment=None,
    )
    db.add(history)

    log_action(
        db,
        user_id=owner.id,
        action="DOCUMENT_CREATED",
        entity_type="DOCUMENT",
        entity_id=str(document.id),
        details={"title": title, "owner_id": str(owner.id), "reviewer_id": str(reviewer.id) if reviewer else None},
    )
    db.commit()
    db.refresh(document)
    return document


def create_new_version(
    db: Session,
    *,
    owner: User,
    document: Document,
    file_meta: FileMeta,
) -> DocumentVersion:
    if document.owner_id != owner.id and owner.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not document owner")

    latest = get_latest_version(db, document.id)
    if not latest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Latest version not found")

    new_version = DocumentVersion(
        document_id=document.id,
        version_number=latest.version_number + 1,
        status=DocumentStatus.DRAFT.value,
        original_filename=file_meta.original_filename,
        file_mime_type=file_meta.file_mime_type,
        file_size_bytes=file_meta.file_size_bytes,
        created_by=owner.id,
    )
    db.add(new_version)
    db.flush()

    history = DocumentHistory(
        document_version_id=new_version.id,
        from_status=latest.status,
        to_status=DocumentStatus.DRAFT.value,
        action="NEW_VERSION",
        actor_user_id=owner.id,
        comment=None,
    )
    db.add(history)

    log_action(
        db,
        user_id=owner.id,
        action="DOCUMENT_NEW_VERSION",
        entity_type="DOCUMENT_VERSION",
        entity_id=str(new_version.id),
        details={"document_id": str(document.id), "version_number": new_version.version_number},
    )
    db.commit()
    db.refresh(new_version)
    return new_version


def submit_document(db: Session, *, actor: User, document: Document, comment: str | None) -> DocumentVersion:
    latest = get_latest_version(db, document.id)
    if not latest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Latest version not found")
    if latest.status != DocumentStatus.DRAFT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only Draft versions can be submitted")
    if document.owner_id != actor.id and actor.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not document owner")

    from_status = latest.status
    latest.status = DocumentStatus.SUBMITTED.value
    latest.reviewed_by = None
    latest.review_comment = None

    history = DocumentHistory(
        document_version_id=latest.id,
        from_status=from_status,
        to_status=DocumentStatus.SUBMITTED.value,
        action="SUBMITTED",
        actor_user_id=actor.id,
        comment=comment,
    )
    db.add(history)

    log_action(
        db,
        user_id=actor.id,
        action="DOCUMENT_SUBMITTED",
        entity_type="DOCUMENT_VERSION",
        entity_id=str(latest.id),
        details={"document_id": str(document.id), "version_number": latest.version_number},
    )
    db.commit()
    db.refresh(latest)
    return latest


def review_document(
    db: Session,
    *,
    reviewer: User,
    document: Document,
    decision: DocumentStatus,
    comment: str | None,
) -> DocumentVersion:
    latest = get_latest_version(db, document.id)
    if not latest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Latest version not found")

    if document.reviewer_id != reviewer.id and reviewer.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not assigned reviewer")
    if latest.status != DocumentStatus.SUBMITTED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only Submitted versions can be reviewed")
    if decision not in (DocumentStatus.APPROVED, DocumentStatus.REJECTED):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid decision")

    from_status = latest.status
    latest.status = decision.value
    latest.reviewed_by = reviewer.id
    latest.review_comment = comment

    history = DocumentHistory(
        document_version_id=latest.id,
        from_status=from_status,
        to_status=decision.value,
        action="APPROVED" if decision == DocumentStatus.APPROVED else "REJECTED",
        actor_user_id=reviewer.id,
        comment=comment,
    )
    db.add(history)

    log_action(
        db,
        user_id=reviewer.id,
        action="DOCUMENT_APPROVED" if decision == DocumentStatus.APPROVED else "DOCUMENT_REJECTED",
        entity_type="DOCUMENT_VERSION",
        entity_id=str(latest.id),
        details={"document_id": str(document.id), "version_number": latest.version_number, "decision": decision.value},
    )
    db.commit()
    db.refresh(latest)
    return latest


def list_documents_for_user(db: Session, *, user: User) -> list[Document]:
    if user.role == UserRole.ADMIN.value:
        return db.query(Document).order_by(Document.updated_at.desc()).all()
    # Researchers can see documents they own; reviewers can see documents assigned to them.
    return (
        db.query(Document)
        .filter((Document.owner_id == user.id) | (Document.reviewer_id == user.id))
        .order_by(Document.updated_at.desc())
        .all()
    )


def get_document(db: Session, *, document_id: UUID, viewer: User) -> Document:
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if viewer.role != UserRole.ADMIN.value and doc.owner_id != viewer.id and (doc.reviewer_id != viewer.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return doc


def get_document_history(db: Session, *, document: Document, viewer: User) -> list[DocumentHistory]:
    # Access control reuses get_document authorization.
    if viewer.role != UserRole.ADMIN.value and document.owner_id != viewer.id and document.reviewer_id != viewer.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return (
        db.query(DocumentHistory)
        .join(DocumentVersion, DocumentHistory.document_version_id == DocumentVersion.id)
        .filter(DocumentVersion.document_id == document.id)
        .order_by(DocumentHistory.created_at.asc())
        .all()
    )


def get_approval_queue(db: Session, *, reviewer: User) -> list[Document]:
    if reviewer.role != UserRole.REVIEWER.value and reviewer.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a reviewer")

    q = db.query(Document).filter(Document.reviewer_id == reviewer.id)
    docs = q.all()
    # Only include where latest version is Submitted.
    out: list[Document] = []
    for d in docs:
        latest = get_latest_version(db, d.id)
        if latest and latest.status == DocumentStatus.SUBMITTED.value:
            out.append(d)
    out.sort(key=lambda d: d.updated_at, reverse=True)
    return out

