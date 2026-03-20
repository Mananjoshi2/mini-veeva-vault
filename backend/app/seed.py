from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import hash_password
from app.db.session import get_sessionmaker
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.enums import DocumentStatus, UserRole
from app.models.patient import PatientRecord
from app.models.user import User
from app.services.document_service import FileMeta, create_document, create_new_version, review_document, submit_document


def seed_database(settings: Settings) -> None:
    SessionLocal = get_sessionmaker(settings)
    with SessionLocal() as db:
        user_count = db.query(User).count()
        if user_count > 0:
            return

        # Users
        researcher = User(
            email="researcher1@miniveeva.local",
            password_hash=hash_password(settings.SEED_USER_PASSWORD),
            role=UserRole.RESEARCHER.value,
        )
        reviewer = User(
            email="reviewer1@miniveeva.local",
            password_hash=hash_password(settings.SEED_USER_PASSWORD),
            role=UserRole.REVIEWER.value,
        )
        admin = User(
            email="admin1@miniveeva.local",
            password_hash=hash_password(settings.SEED_USER_PASSWORD),
            role=UserRole.ADMIN.value,
        )
        db.add_all([researcher, reviewer, admin])
        db.commit()
        db.refresh(researcher)
        db.refresh(reviewer)
        db.refresh(admin)

        # Patients
        now = datetime.now(timezone.utc)
        patients = []
        for i in range(10):
            ts = now - timedelta(days=i * 2)
            treatment = "Atezolizumab" if i % 2 == 0 else "Pembrolizumab"
            outcome = "Improved" if i % 3 == 0 else "Stable" if i % 3 == 1 else "Progressed"
            patients.append(PatientRecord(treatment=treatment, outcome=outcome, timestamp=ts))
        db.add_all(patients)
        db.commit()

        # Documents (Researcher -> Draft -> Submitted -> Reviewer Approved/Rejected)
        file_meta_none = FileMeta(original_filename=None, file_mime_type=None, file_size_bytes=None)

        doc_approved = create_document(
            db,
            owner=researcher,
            reviewer=reviewer,
            title="Protocol Amendment v1",
            description="Initial amendment draft for review.",
            file_meta=file_meta_none,
        )
        latest = (
            db.query(DocumentVersion)
            .filter(DocumentVersion.document_id == doc_approved.id)
            .order_by(DocumentVersion.version_number.desc())
            .first()
        )
        if latest:
            submit_document(db, actor=researcher, document=doc_approved, comment="Submitting for regulatory review.")
            review_document(
                db,
                reviewer=reviewer,
                document=doc_approved,
                decision=DocumentStatus.APPROVED,
                comment="Approved; proceed to next trial step.",
            )

        doc_rejected = create_document(
            db,
            owner=researcher,
            reviewer=reviewer,
            title="Informed Consent Update v1",
            description="Updated consent language; pending review.",
            file_meta=file_meta_none,
        )
        submit_document(db, actor=researcher, document=doc_rejected, comment="Submitting consent update.")
        review_document(
            db,
            reviewer=reviewer,
            document=doc_rejected,
            decision=DocumentStatus.REJECTED,
            comment="Rejected: missing required sections in appendix.",
        )
        # Create a new version after rejection.
        create_new_version(
            db,
            owner=researcher,
            document=doc_rejected,
            file_meta=FileMeta(original_filename=None, file_mime_type=None, file_size_bytes=None),
        )
        submit_document(db, actor=researcher, document=doc_rejected, comment="Resubmitting revised version.")
        review_document(
            db,
            reviewer=reviewer,
            document=doc_rejected,
            decision=DocumentStatus.APPROVED,
            comment="Approved after revisions.",
        )

        # Another document with multiple versions.
        doc_multi = create_document(
            db,
            owner=researcher,
            reviewer=reviewer,
            title="Safety Report v1",
            description="Quarterly safety report; versioned submissions.",
            file_meta=file_meta_none,
        )
        create_new_version(
            db,
            owner=researcher,
            document=doc_multi,
            file_meta=file_meta_none,
        )
        submit_document(db, actor=researcher, document=doc_multi, comment="Submitting the latest safety report version.")
        review_document(
            db,
            reviewer=reviewer,
            document=doc_multi,
            decision=DocumentStatus.APPROVED,
            comment="Approved.",
        )

