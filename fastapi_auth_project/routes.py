from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from created_models.user import User
from created_models.token_black_list import TokenBlacklist
from created_models.user_role import UserRole
from schemas import UserCreate, UserResponse, LoginRequest, TokenResponse, MessageResponse
from fastapi.security import HTTPAuthorizationCredentials
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, bearer_scheme, require_admin, require_user
)

router = APIRouter(prefix="/auth", tags=["--Authentication--"])
admin_router = APIRouter(prefix="/admin", tags=["Admin Only"])
user_router = APIRouter(prefix="/user", tags=["User"])


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
        hashed_password=hash_password(user_data.password),
        role=UserRole.USER   # always force USER — never trust client-sent role

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

    # Blacklist old token only if not already blacklisted
    if user.current_token:
        already_blacklisted = db.query(TokenBlacklist).filter(
        TokenBlacklist.token == user.current_token
    ).first()
        if not already_blacklisted:
            db.add(TokenBlacklist(token=user.current_token))


    # Create new token
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role.value   # role is embedded in the token
            },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Save new token
    user.current_token = access_token
    db.commit()

    return {"access_token": access_token, "token_type": "bearer", "role": user.role}


@router.post("/logout", response_model=MessageResponse)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print("\n\n\n\n========creds====", credentials, "\n\n\n\n")
    """
    Logout the current user.
    JWTs can't be 'deleted' since they're stateless.
    Solution: store the token in a blacklist table.
    get_current_user checks this blacklist on every request.
    """
    token = credentials.credentials
    # Check if already blacklisted
    already_blacklisted = db.query(TokenBlacklist).filter(
        TokenBlacklist.token == token
    ).first()
    
    if already_blacklisted:
        raise HTTPException(
            status_code=400,
            detail="Token already invalidated"
        )


    blacklisted = TokenBlacklist(token=token)
    db.add(blacklisted)
    db.commit()

    return {"message": "Successfully logged out"}


# @router.get("/me", response_model=UserResponse)
# def get_me(current_user: User = Depends(get_current_user)):
#     """
#     Get the currently logged-in user's info.
#     get_current_user dependency handles all auth checking.
#     If token is invalid/expired/blacklisted → 401 automatically.
#     """
#     return current_user


# ─────────────────────────────────────────────
#  USER ROUTES (both user and admin allowed)
# ─────────────────────────────────────────────

@user_router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(require_user)):
    """Any logged-in user can view their own profile."""
    return current_user


@user_router.put("/me", response_model=UserResponse)
def update_my_profile(
    update_data: dict,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Any logged-in user can update their own profile."""
    allowed_fields = {"email", "username"}
    for field, value in update_data.items():
        if field in allowed_fields:
            setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


# ─────────────────────────────────────────────
#  ADMIN ROUTES (admin only)
# ─────────────────────────────────────────────

@admin_router.get("/users", response_model=list[UserResponse])
def list_all_users(
    current_user: User = Depends(require_admin),  # blocks non-admins
    db: Session = Depends(get_db)
):
    """
    Admin only — list every user in the system.
    A regular user hitting this gets 403 Forbidden.
    """
    return db.query(User).all()


@admin_router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin only — delete any user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(400, "Cannot delete your own account")

    db.delete(user)
    db.commit()
    return {"message": f"User '{user.username}' deleted"}


@admin_router.patch("/users/{user_id}/role", response_model=UserResponse)
def change_user_role(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin only — promote a user to admin or demote admin to user.
    This is the ONLY way someone becomes an admin.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


@admin_router.patch("/users/{user_id}/deactivate", response_model=MessageResponse)
def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin only — deactivate a user account without deleting it."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    user.is_active = False
    db.commit()
    return {"message": f"User '{user.username}' deactivated"}
