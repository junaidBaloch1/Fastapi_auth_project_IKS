from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from created_models.user_role import UserRole

class UserCreate(BaseModel):
    """
    Schema for INCOMING register request.
    Pydantic validates this automatically — wrong types = 422 error.
    """
    username: str
    email: EmailStr       # validates email format automatically
    password: str
    # role is optional — if not provided, defaults to "user"
    # admins are created by other admins, not by self-registration
    role: UserRole = UserRole.USER



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
    role: UserRole          # now included in response

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy model directly


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    """Returned after successful login."""
    access_token: str
    token_type: str = "bearer"
    role: UserRole          # return role on login so client knows what UI to show



class MessageResponse(BaseModel):
    """Generic response for logout etc."""
    message: str