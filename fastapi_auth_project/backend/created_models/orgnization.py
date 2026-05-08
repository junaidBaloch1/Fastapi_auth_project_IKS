from sqlalchemy import (Column, Boolean, Integer, String, DateTime, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Organization(Base):
    """
    Each admin owns one or more organizations.
    created_by links back to the admin User who created it.
    """
    __tablename__ = "organizations"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(255), unique=True, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    is_active = Column(Boolean, default=True)


    # relationships
    creator   = relationship("User",       foreign_keys=[created_by])
    members = relationship("OrgMember",  back_populates="organization")
    invitations = relationship("Invitation", back_populates="organization")
