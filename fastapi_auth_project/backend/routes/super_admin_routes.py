from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from created_models.user import User 
from created_models.orgnization import Organization
from created_models.org_member import OrgMember 
from created_models.invitation import Invitation
from created_models.user_role import UserRole
from schemas import UserResponse, OrgResponse, MessageResponse
from auth import require_super_admin

super_router = APIRouter(prefix="/super", tags=["Super Admin"])


# ═══════════════════════════════════════════════
#  USER MANAGEMENT
# ═══════════════════════════════════════════════

@super_router.get("/users", response_model=list[UserResponse])
def list_all_users(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """List every user in the system regardless of role."""
    return db.query(User).filter(User.is_active == True).all()


@super_router.get("/users/admins", response_model=list[UserResponse])
def list_all_admins(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """List every admin in the system."""
    return db.query(User).filter(User.role == UserRole.ADMIN, User.is_active == True).all()


@super_router.get("/users/no-org", response_model=list[UserResponse])
def users_not_in_any_org(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    List all users who are not a member of any organization.
    Uses a subquery — first get all user_ids that ARE in org_members,
    then return users whose id is NOT in that set.
    """
    # subquery: all user_ids that have at least one org membership
    member_user_ids = db.query(OrgMember.user_id).distinct().subquery()

    # users whose id is not in that subquery
    return db.query(User).filter(
        User.id.not_in(member_user_ids),
        User.role == UserRole.USER   # only regular users, not admins
    ).all()


@super_router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_admin(
    user_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Delete an admin account.
    Also cascades — their organizations and invitations are deleted.
    Super admin cannot delete themselves.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    if user.id == current_user.id:
        raise HTTPException(400, "Cannot delete your own account")

    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(400, "Cannot delete another super admin")

    # db.delete(user)
    user.is_active = False
    db.commit()
    return {"message": f"User  admin '{user.username}' inactive and all their data deleted"}


@super_router.patch("/users/{user_id}/role", response_model=UserResponse)
def change_user_role(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Promote or demote any user to any role.
    This is the ONLY way to create a new super_admin or admin.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    if user.id == current_user.id:
        raise HTTPException(400, "Cannot change your own role")

    old_role = user.role
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


# ═══════════════════════════════════════════════
#  ORGANIZATION MANAGEMENT
# ═══════════════════════════════════════════════

@super_router.get("/orgs", response_model=list[OrgResponse])
def list_all_orgs(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """List every organization in the system."""
    return db.query(Organization).filter(Organization.is_active == True).all()


@super_router.get("/orgs/{org_id}/users", response_model=list[UserResponse])
def users_in_org(
    org_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    List all users that belong to a specific organization.
    Joins OrgMember → User to get full user details.
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Organization not found")

    members = db.query(OrgMember).filter(OrgMember.org_id == org_id).all()
    return [m.user for m in members]


@super_router.get("/admins/{admin_id}/orgs", response_model=list[OrgResponse])
def get_admin_orgs(
    admin_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """List all organizations owned by a specific admin."""
    admin = db.query(User).filter(
        User.id == admin_id,
        User.role == UserRole.ADMIN
    ).first()
    if not admin:
        raise HTTPException(404, "Admin not found")

    return db.query(Organization).filter(
        Organization.created_by == admin_id
    ).all()


@super_router.delete("/orgs/{org_id}", response_model=MessageResponse)
def delete_org(
    org_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Delete any organization.
    Cascades: all memberships and invitations for this org are deleted too.
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Organization not found")

    org_name = org.name
    # db.delete(org)
    org.is_active = False
    db.commit()
    return {"message": f"Organization '{org_name}' deleted"}


@super_router.delete("/orgs/{org_id}/members/{user_id}", response_model=MessageResponse)
def remove_member_from_org(
    org_id: int,
    user_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Super admin removes any user from any organization."""
    member = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(404, "Member not found in this organization")

    # db.delete(member)
    member.is_active = False
    db.commit()
    return {"message": "Member inactive removed from organization"}


# ═══════════════════════════════════════════════
#  STATS OVERVIEW
# ═══════════════════════════════════════════════

@super_router.get("/stats")
def system_stats(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Quick system overview for the super admin dashboard.
    Returns counts of all major entities in one call.
    """
    total_users  = db.query(func.count(User.id)).filter(User.role == UserRole.USER).scalar()
    total_admins = db.query(func.count(User.id)).filter(User.role == UserRole.ADMIN).scalar()
    total_orgs   = db.query(func.count(Organization.id)).scalar()
    total_members = db.query(func.count(OrgMember.id)).scalar()

    # users not in any org
    member_ids   = db.query(OrgMember.user_id).distinct().subquery()
    users_no_org = db.query(func.count(User.id)).filter(
        User.id.not_in(member_ids),
        User.role == UserRole.USER
    ).scalar()

    return {
        "total_users":        total_users,
        "total_admins":       total_admins,
        "total_orgs":         total_orgs,
        "total_memberships":  total_members,
        "users_without_org":  users_no_org,
    }