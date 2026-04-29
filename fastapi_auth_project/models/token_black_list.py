from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base



class TokenBlacklist(Base):
    """
    Stores invalidated JWT tokens after logout.
    When a user logs out, their token is added here.
    On every request, we check this table — if the token is here, reject it.
    This is how logout works with stateless JWTs.
    """
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())