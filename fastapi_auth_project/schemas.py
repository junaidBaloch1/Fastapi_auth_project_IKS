from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from created_models.user_role import UserRole
from created_models.invitation import InvitationStatus

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

# ── organization schemas ──────────────────────────────

class OrgCreate(BaseModel):
    """Admin sends just a name to create an org."""
    name: str

class OrgResponse(BaseModel):
    id: int
    name: str
    created_by: int
    created_at: datetime
    class Config:
        from_attributes = True

class OrgMemberResponse(BaseModel):
    """Represents one member inside an org."""
    id: int
    user_id: int
    org_id: int
    joined_at: datetime
    user: UserResponse          # nested — shows full user info
    class Config:
        from_attributes = True


# ── invitation schemas ────────────────────────────────

class InvitationCreate(BaseModel):
    """Admin sends user_id and org_id to invite someone."""
    invited_user_id: int
    org_id: int

class InvitationResponse(BaseModel):
    id: int
    org_id: int
    invited_user_id: int
    invited_by_id: int
    status: InvitationStatus
    created_at: datetime
    responded_at: Optional[datetime]
    organization: OrgResponse   # nested — user sees which org invited them
    invited_by: UserResponse    # nested — user sees who sent the invite
    class Config:
        from_attributes = True
