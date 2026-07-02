"""
schemas/user.py
Pydantic schemas for authentication and user management.
UserCreate accepts plain password — UserResponse never exposes it.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration — accepts plain password."""
    username:  str
    email:     EmailStr
    password:  str


class UserResponse(BaseModel):
    """Schema for user API responses — password never included."""
    id:       int
    username: str
    email:    EmailStr
    role:     str
    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema returned on successful login."""
    access_token: str
    token_type:   str = "bearer"


class TokenData(BaseModel):
    """Internal schema — decoded JWT payload."""
    email: Optional[str] = None