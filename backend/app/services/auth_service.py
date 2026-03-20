from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.auth import SignupRequest


def signup(db: Session, settings: Settings, req: SignupRequest) -> tuple[User, str]:
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if req.role is None or not settings.ROLE_ASSIGNMENT_ON_SIGNUP:
        role = UserRole.RESEARCHER.value
    else:
        role = UserRole(req.role).value

    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(settings=settings, subject=str(user.id), role=user.role)
    return user, token


def authenticate(db: Session, settings: Settings, email: str, password: str) -> tuple[User, str]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(settings=settings, subject=str(user.id), role=user.role)
    return user, token

