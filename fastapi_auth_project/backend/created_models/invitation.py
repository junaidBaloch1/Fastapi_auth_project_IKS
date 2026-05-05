from sqlalchemy import (Column, Integer, DateTime, Enum, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class InvitationStatus(str, enum.Enum):
    PENDING  = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class Invitation(Base):
    """
    Represents an invitation sent from an org (by its admin) to a user.
    Status starts as PENDING.
    On accept  → OrgMember row is created, status → ACCEPTED.
    On decline → status → DECLINED, no OrgMember created.
    """
    __tablename__ = "invitations"

    id              = Column(Integer, primary_key=True, index=True)
    org_id          = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    invited_user_id = Column(Integer, ForeignKey("users.id"),         nullable=False)
    invited_by_id   = Column(Integer, ForeignKey("users.id"),         nullable=False)
    status          = Column(Enum(InvitationStatus), default=InvitationStatus.PENDING, server_default="pending", nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    responded_at    = Column(DateTime(timezone=True), nullable=True)

    organization  = relationship("Organization", back_populates="invitations")
    invited_user  = relationship("User", back_populates="received_invitations", foreign_keys=[invited_user_id])
    invited_by    = relationship("User", foreign_keys=[invited_by_id])
