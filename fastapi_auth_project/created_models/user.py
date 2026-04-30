from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
from created_models.user_role import UserRole


class User(Base):
    """
    Maps to the 'users' table in the database.
    Each column = one field on the table.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)  # never store plain password
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    current_token = Column(String(255), nullable=True)

    # New: role column — defaults to "user" for every new registration
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False, server_default="user")
