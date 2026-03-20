from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.base import Base
from app.db.session import get_engine
from app.seed import seed_database
from app.routes.auth_routes import router as auth_router
from app.routes.patient_routes import router as patient_router
from app.routes.document_routes import router as document_router
from app.routes.audit_routes import router as audit_router

# Import models so SQLAlchemy registers them with Base.metadata.
from app.models import enums as _enums  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.patient import PatientRecord  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.document_version import DocumentVersion  # noqa: F401
from app.models.document_history import DocumentHistory  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(title="Mini Veeva Vault")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(patient_router)
    app.include_router(document_router)
    app.include_router(audit_router)

    @app.on_event("startup")
    def on_startup() -> None:
        engine = get_engine(settings)
        Base.metadata.create_all(bind=engine)
        if settings.SEED_ON_STARTUP:
            seed_database(settings)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()

