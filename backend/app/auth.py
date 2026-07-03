"""
auth.py
Core authentication logic — password hashing, JWT creation/verification,
and the get_current_user FastAPI dependency.
This file is security-critical — every line matters.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db, settings
from app.models import User


# ── Passlib context ───────────────────────────────────────────────────────────
# bcrypt is the hashing scheme. deprecated="auto" handles old hash formats.

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# ── OAuth2 scheme ─────────────────────────────────────────────────────────────
# Reads "Authorization: Bearer <token>" from request headers.

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── Reusable 401 exception ────────────────────────────────────────────────────
# WWW-Authenticate header is part of the HTTP auth standard.

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)


# ── Password utils ────────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Hash a plain text password using bcrypt."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT utils ─────────────────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """
    Create a signed JWT token.
    Adds expiry time to the payload before signing.
    """
    to_encode = data.copy()
    expiry = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode["exp"] = expiry
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> Optional[str]:
    """
    Decode and verify a JWT token.
    Returns the email (sub claim) or None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload.get("sub")
    except JWTError:
        return None


# ── FastAPI dependency ────────────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency injected into every protected endpoint.
    Decodes token → fetches user from DB → returns User object.
    Raises 401 if token is invalid, expired, or user not found.
    """
    email = decode_access_token(token)
    if not email:
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )
    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact admin.",
        )
    return user


# ── Public interface ──────────────────────────────────────────────────────────

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "oauth2_scheme",
]