from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.deps import get_db, get_current_user, get_settings
from app.models.enums import UserRole
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserOut
from app.services.auth_service import authenticate, signup


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
def api_signup(
    req: SignupRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    user, token = signup(db, settings, req)
    return TokenResponse(access_token=token, user=UserOut(id=user.id, email=user.email, role=UserRole(user.role)))


@router.post("/login", response_model=TokenResponse)
def api_login(
    req: LoginRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    user, token = authenticate(db, settings, email=req.email, password=req.password)
    return TokenResponse(access_token=token, user=UserOut(id=user.id, email=user.email, role=UserRole(user.role)))


@router.get("/me")
def api_me(current_user=Depends(get_current_user)):
    return UserOut(id=current_user.id, email=current_user.email, role=UserRole(current_user.role))

