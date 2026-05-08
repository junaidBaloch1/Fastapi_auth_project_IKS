from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from created_models.user import User
from created_models.token_black_list import TokenBlacklist
from created_models.user_role import UserRole
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Secret key — in production, load from environment variable, never hardcode
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# bcrypt context — handles hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Tells FastAPI where to find the token (looks in Authorization header)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    """Convert plain password → bcrypt hash."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Check if plain password matches stored hash."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT token.
    'data' is the payload — we put username inside.
    The token is signed with SECRET_KEY so it can't be tampered with.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    """
    Dependency — called automatically on protected routes.
    1. Checks token is not blacklisted (user logged out)
    2. Decodes and validates the JWT
    3. Fetches and returns the user from DB

    If anything fails → 401 Unauthorized
    """
    # extract token from credetials object
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Check if token was blacklisted (user logged out)
    blacklisted = db.query(TokenBlacklist).filter(
        TokenBlacklist.token == token
    ).first()
    if blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated. Please log in again. already blacklisted token"
        )

    try:
        # Decode the JWT — raises JWTError if invalid or expired
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")  # "sub" is standard JWT claim for subject
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.username == username).first()

    if user is None:
        raise credentials_exception
    
    # 🔥 NEW CHECK (important for single active session)
    if user.current_token != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again."
        )
    
    return user

def require_role(*roles: UserRole):
    """
    Role-checking dependency factory.

    Usage:
        Depends(require_role(UserRole.ADMIN))
        Depends(require_role(UserRole.ADMIN, UserRole.USER))

    How it works:
        require_role() returns a function.
        FastAPI calls that function as a dependency.
        The function checks if the current user's role is in the allowed list.
        If not → 403 Forbidden.

    This pattern is called a 'dependency factory' — a function that
    returns a dependency function. It lets us pass arguments (the roles)
    to a dependency.
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {[r.value for r in roles]}"
            )
        return current_user
    return role_checker


# Convenience shortcuts — use these in routes
require_super_admin = require_role(UserRole.SUPER_ADMIN)
require_admin = require_role(UserRole.ADMIN)
require_user  = require_role(UserRole.USER, UserRole.ADMIN, UserRole.SUPER_ADMIN)  # admin  and super admin can do user things too
require_admin_or_super = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
