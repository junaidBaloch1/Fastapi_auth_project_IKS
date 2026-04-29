from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from models.user import User
from models.token_black_list import TokenBlacklist
from schemas import UserCreate, UserResponse, LoginRequest, TokenResponse, MessageResponse
from fastapi.security import HTTPAuthorizationCredentials
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, bearer_scheme
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    - Checks username and email are unique
    - Hashes the password
    - Saves user to database
    - Returns user info (no password)
    """
    # Check username not taken
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check email not taken
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user with hashed password
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # refresh to get auto-generated fields like id, created_at

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with username and password.
    - Finds user in DB
    - Verifies password against stored hash
    - Returns JWT access token
    """
    user = db.query(User).filter(User.username == login_data.username).first()

    # Same error for wrong username OR wrong password
    # Never reveal which one is wrong — security best practice
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    # validate old token (if exists)
    if user.current_token:
        db.add(TokenBlacklist(token=user.current_token))

    # Create new token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    print("\n\n\n access token====", access_token, "=====\n\n\n")
    # Save new token
    user.current_token = access_token
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", response_model=MessageResponse)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout the current user.
    JWTs can't be 'deleted' since they're stateless.
    Solution: store the token in a blacklist table.
    get_current_user checks this blacklist on every request.
    """
    blacklisted = TokenBlacklist(token=credentials)
    db.add(blacklisted)
    db.commit()

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the currently logged-in user's info.
    get_current_user dependency handles all auth checking.
    If token is invalid/expired/blacklisted → 401 automatically.
    """
    return current_user