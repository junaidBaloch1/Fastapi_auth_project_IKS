from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """
    Schema for INCOMING register request.
    Pydantic validates this automatically — wrong types = 422 error.
    """
    username: str
    email: EmailStr       # validates email format automatically
    password: str


class UserResponse(BaseModel):
    """
    Schema for OUTGOING user data.
    Notice: no password field — we never send it back.
    """
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy model directly


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    """Returned after successful login."""
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Generic response for logout etc."""
    message: str