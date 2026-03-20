from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user, require_roles
from app.models.document import Document
from app.models.document_history import DocumentHistory
from app.models.document_version import DocumentVersion
from app.models.enums import DocumentStatus, UserRole
from app.models.user import User
from app.schemas.document import (
    DocumentCreateRequest,
    DocumentHistoryEventOut,
    DocumentListItemOut,
    DocumentOut,
    DocumentReviewRequest,
    DocumentSubmitRequest,
    DocumentVersionOut,
)
from app.services.document_service import (
    FileMeta,
    create_document,
    create_new_version,
    get_approval_queue,
    get_document,
    get_document_history,
    get_latest_version,
    list_documents_for_user,
    review_document,
    submit_document,
)


router = APIRouter(prefix="/api/documents", tags=["documents"])


def _to_version_out(version: DocumentVersion) -> DocumentVersionOut:
    return DocumentVersionOut(
        id=version.id,
        document_id=version.document_id,
        version_number=version.version_number,
        status=DocumentStatus(version.status),
        original_filename=version.original_filename,
        created_by=version.created_by,
        created_at=version.created_at,
        reviewed_by=version.reviewed_by,
        review_comment=version.review_comment,
    )


@router.post("", response_model=DocumentOut, status_code=201)
def api_create_document(
    title: str = Form(...),
    reviewer_email: str | None = Form(None),
    description: str | None = Form(None),
    document_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role not in (UserRole.RESEARCHER.value, UserRole.ADMIN.value):
        raise HTTPException(status_code=403, detail="Not allowed")

    reviewer: User | None = None
    if reviewer_email:
        reviewer = db.query(User).filter(User.email == reviewer_email).first()
        if not reviewer:
            raise HTTPException(status_code=400, detail="Reviewer email not found")

    content = document_file.file.read()
    file_meta = FileMeta(
        original_filename=document_file.filename,
        file_mime_type=document_file.content_type,
        file_size_bytes=len(content) if content is not None else None,
    )

    doc = create_document(
        db,
        owner=current_user,
        reviewer=reviewer,
        title=title,
        description=description,
        file_meta=file_meta,
    )
    latest = get_latest_version(db, doc.id)
    if not latest:
        raise HTTPException(status_code=500, detail="Version missing after create")
    return DocumentOut(
        id=doc.id,
        title=doc.title,
        owner_id=doc.owner_id,
        reviewer_id=doc.reviewer_id,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        current_version=_to_version_out(latest),
    )


@router.get("", response_model=list[DocumentListItemOut])
def api_list_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    docs = list_documents_for_user(db, user=current_user)
    out: list[DocumentListItemOut] = []
    for d in docs:
        latest = get_latest_version(db, d.id)
        if not latest:
            continue
        out.append(
            DocumentListItemOut(
                id=d.id,
                title=d.title,
                owner_id=d.owner_id,
                reviewer_id=d.reviewer_id,
                current_version_number=latest.version_number,
                current_status=DocumentStatus(latest.status),
                updated_at=d.updated_at,
            )
        )
    return out


@router.get("/{document_id}", response_model=DocumentOut)
def api_get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    doc = get_document(db, document_id=document_id, viewer=current_user)
    latest = get_latest_version(db, doc.id)
    if not latest:
        raise HTTPException(status_code=404, detail="Latest version missing")
    return DocumentOut(
        id=doc.id,
        title=doc.title,
        owner_id=doc.owner_id,
        reviewer_id=doc.reviewer_id,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        current_version=_to_version_out(latest),
    )


@router.post("/{document_id}/versions", response_model=DocumentVersionOut, status_code=201)
def api_new_version(
    document_id: UUID,
    document_file: UploadFile = File(...),
    description: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.RESEARCHER, UserRole.ADMIN)),
):
    doc: Document | None = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    content = document_file.file.read()
    file_meta = FileMeta(
        original_filename=document_file.filename,
        file_mime_type=document_file.content_type,
        file_size_bytes=len(content) if content is not None else None,
    )

    latest = create_new_version(db, owner=current_user, document=doc, file_meta=file_meta)
    # Optionally update document description.
    if description is not None and description != doc.description:
        doc.description = description
        db.add(doc)
        db.commit()
        db.refresh(doc)

    return _to_version_out(latest)


@router.post("/{document_id}/submit", response_model=DocumentVersionOut)
def api_submit_document(
    document_id: UUID,
    payload: DocumentSubmitRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.RESEARCHER, UserRole.ADMIN)),
):
    doc: Document | None = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    latest = submit_document(db, actor=current_user, document=doc, comment=payload.comment)
    return _to_version_out(latest)


@router.post("/{document_id}/review", response_model=DocumentVersionOut)
def api_review_document(
    document_id: UUID,
    payload: DocumentReviewRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.REVIEWER, UserRole.ADMIN)),
):
    doc: Document | None = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    decision = DocumentStatus.APPROVED if payload.decision == "Approved" else DocumentStatus.REJECTED
    latest = review_document(db, reviewer=current_user, document=doc, decision=decision, comment=payload.comment)
    return _to_version_out(latest)


@router.get("/{document_id}/history", response_model=list[DocumentHistoryEventOut])
def api_document_history(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    doc = get_document(db, document_id=document_id, viewer=current_user)
    events = get_document_history(db, document=doc, viewer=current_user)
    return [
        DocumentHistoryEventOut(
            id=e.id,
            document_version_id=e.document_version_id,
            from_status=e.from_status,
            to_status=e.to_status,
            action=e.action,
            actor_user_id=e.actor_user_id,
            comment=e.comment,
            created_at=e.created_at,
        )
        for e in events
    ]


@router.get("/approvals/queue", response_model=list[DocumentListItemOut])
def api_approval_queue(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.REVIEWER, UserRole.ADMIN)),
):
    docs = get_approval_queue(db, reviewer=current_user)
    out: list[DocumentListItemOut] = []
    for d in docs:
        latest = get_latest_version(db, d.id)
        if not latest:
            continue
        out.append(
            DocumentListItemOut(
                id=d.id,
                title=d.title,
                owner_id=d.owner_id,
                reviewer_id=d.reviewer_id,
                current_version_number=latest.version_number,
                current_status=DocumentStatus(latest.status),
                updated_at=d.updated_at,
            )
        )
    return out

