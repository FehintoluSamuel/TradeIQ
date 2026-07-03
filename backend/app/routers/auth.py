"""
routers/auth.py
Authentication endpoints — signup, login, and current user profile.
All password logic delegated to app/auth.py.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, TokenResponse


router = APIRouter()


# ── Signup ────────────────────────────────────────────────────────────────────

@router.post("/auth/signup", response_model=UserResponse, status_code=201)
def signup(data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    Returns the created user profile — never the password.
    """
    # Check email not already registered
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Check username not already taken
    existing_username = db.query(User).filter(User.username == data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken.",
        )

    new_user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        # role and is_active use model defaults — user cannot set these
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # loads DB-generated fields: id, created_at
    return new_user


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/auth/login", response_model=TokenResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return a JWT access token.
    form.username holds the email — OAuth2 standard field naming.
    Always return the same vague error for wrong email OR wrong password.
    Never reveal which field is incorrect — prevents user enumeration attacks.
    """
    user = db.query(User).filter(User.email == form.username).first()

    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact admin.",
        )

    token = create_access_token({"sub": user.email})
    return TokenResponse(access_token=token, token_type="bearer")


# ── Current user ──────────────────────────────────────────────────────────────

@router.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Return the currently authenticated user's profile.
    Protected — requires valid JWT token in Authorization header.
    """
    return current_user