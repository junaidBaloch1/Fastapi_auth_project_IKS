from sqlalchemy import (Column, Integer, DateTime, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class OrgMember(Base):
    """
    Junction table — links Users to Organizations.
    A user can belong to multiple orgs.
    An org can have multiple users.
    Created when an invitation is accepted.
    """
    __tablename__ = "org_members"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"),         nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organizations")

