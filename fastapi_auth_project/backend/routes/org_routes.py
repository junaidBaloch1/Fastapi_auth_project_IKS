from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import get_db
from created_models.user import User 
from created_models.orgnization import Organization
from created_models.org_member import OrgMember
from created_models.invitation import  Invitation, InvitationStatus
from created_models.user_role import UserRole
from schemas import (
    OrgCreate, OrgResponse, OrgMemberResponse,
    InvitationCreate, InvitationResponse, MessageResponse
)
from auth import require_admin, require_user, get_current_user

org_router = APIRouter(prefix="/org", tags=["Organization"])
invite_router = APIRouter(prefix="/invitations", tags=["Invitations"])


# ═══════════════════════════════════════════════
#  ORGANIZATION ROUTES  (admin only)
# ═══════════════════════════════════════════════

@org_router.post("/", response_model=OrgResponse, status_code=201)
def create_organization(
    data: OrgCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin creates an organization.
    The org is linked to the admin who created it via created_by.
    An admin can own multiple organizations.
    """
    # Check name is unique
    existing = db.query(Organization).filter(
        Organization.name == data.name
    ).first()
    if existing:
        raise HTTPException(400, "Organization name already taken")

    org = Organization(
        name=data.name,
        created_by=current_user.id   # link to the admin
    )
    db.add(org)
    db.flush()  # generates org.id without full commit

    # Now use org.id for admin member
    admin_member = OrgMember(org_id=org.id, user_id=current_user.id)
    db.add(admin_member)

    db.commit()
    db.refresh(org)
    return org



@org_router.get("/my", response_model=list[OrgResponse])
def get_my_organizations(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin sees all organizations they own."""
    return db.query(Organization).filter(
        Organization.created_by == current_user.id
    ).all()


@org_router.get("/{org_id}/members", response_model=list[OrgMemberResponse])
def get_org_members(
    org_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin sees all members of their organization.
    First checks the org belongs to this admin — not any org.
    """
    org = db.query(Organization).filter(
        Organization.id == org_id,
        Organization.created_by == current_user.id  # must own it
    ).first()

    if not org:
        raise HTTPException(404, "Organization not found or not yours")

    # Check if admin is already a member
    admin_already_member = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == current_user.id
    ).first()

    # If not — add them to OrgMember table
    if not admin_already_member:
        admin_member = OrgMember(
            org_id=org_id,
            user_id=current_user.id
        )
        db.add(admin_member)
        db.commit()

    # Now query all members — admin is guaranteed to be there
    members = db.query(OrgMember).filter(
    OrgMember.org_id == org_id,
    OrgMember.is_active == True).all()


    return members


@org_router.delete("/{org_id}/members/{user_id}", response_model=MessageResponse)
def remove_member(
    org_id: int,
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin removes a member from their organization."""
    org = db.query(Organization).filter(
        Organization.id == org_id,
        Organization.created_by == current_user.id
    ).first()
    if not org:
        raise HTTPException(404, "Organization not found or not yours")

    member = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(404, "Member not found in this organization")

    # prevent admin removing themselves
    if member.user_id == current_user.id:
        raise HTTPException(400, "Admin cannot remove themselves")

    # db.delete(member)
    member.is_active = False
    db.commit()
    return {"message": "Member removed inactive from organization"}


# ═══════════════════════════════════════════════
#  INVITATION ROUTES
# ═══════════════════════════════════════════════

@invite_router.post("/", response_model=InvitationResponse, status_code=201)
def send_invitation(
    data: InvitationCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin sends invitation to a user.
    Checks:
      1. The org belongs to this admin
      2. The user exists
      3. User isn't already a member
      4. No pending invitation already exists for this user+org
    """
    # Verify admin owns the org
    org = db.query(Organization).filter(
        Organization.id == data.org_id,
        Organization.created_by == current_user.id
    ).first()
    if not org:
        raise HTTPException(404, "Organization not found or not yours")
    
    # ← key change: find user by email instead of id
    invited_user = db.query(User).filter(
        User.email == data.invited_user_email
    ).first()
    if not invited_user:
        raise HTTPException(404, f"No user found with email {data.invited_user_email}")

   
    # Prevent admin from inviting themselves
    if invited_user.id == current_user.id:
        raise HTTPException(
        status_code=400,
        detail="Admin cannot invite themselves"
    )


    # # Verify target user exists
    # invited_user = db.query(User).filter(
    #     User.id == data.invited_user_id
    # ).first()
    # if not invited_user:
    #     raise HTTPException(404, "User not found")

    # Check user isn't already a member
    already_member = db.query(OrgMember).filter(
        OrgMember.org_id == data.org_id,
        OrgMember.user_id == invited_user.id,
        OrgMember.is_active == True
    ).first()
    if already_member:
        raise HTTPException(400, "User is already a member of this organization")

    # Check no pending invitation already exists
    pending = db.query(Invitation).filter(
        Invitation.org_id == data.org_id,
        Invitation.invited_user_id == invited_user.id,
        Invitation.status == InvitationStatus.PENDING
    ).first()
    if pending:
        raise HTTPException(400, "A pending invitation already exists for this user")

    invitation = Invitation(
        org_id=data.org_id,
        invited_user_id=invited_user.id,
        invited_by_id=current_user.id,
        status=InvitationStatus.PENDING
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation


@invite_router.get("/sent", response_model=list[InvitationResponse])
def get_sent_invitations(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin sees all invitations they have sent across all their orgs."""
    return db.query(Invitation).filter(
        Invitation.invited_by_id == current_user.id
    ).all()


@invite_router.delete("/{invitation_id}", response_model=MessageResponse)
def cancel_invitation(
    invitation_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin cancels a pending invitation they sent."""
    invitation = db.query(Invitation).filter(
        Invitation.id == invitation_id,
        Invitation.invited_by_id == current_user.id,
        Invitation.status == InvitationStatus.PENDING  # can only cancel pending
    ).first()
    if not invitation:
        raise HTTPException(404, "Pending invitation not found")

    db.delete(invitation)
    db.commit()
    return {"message": "Invitation cancelled"}


# ── user side ──────────────────────────────────────────

@invite_router.get("/my", response_model=list[InvitationResponse])
def get_my_invitations(
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    User sees all invitations received — pending, accepted, declined.
    The response includes the org name and who sent it,
    so the user has full context to decide.
    """
    return db.query(Invitation).filter(
        Invitation.invited_user_id == current_user.id
    ).all()


@invite_router.post("/{invitation_id}/accept", response_model=MessageResponse)
def accept_invitation(
    invitation_id: int,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    User accepts an invitation.
    Two things happen atomically:
      1. Invitation status → ACCEPTED
      2. OrgMember row created → user joins the org
    If the DB fails midway, both changes roll back together.
    """
    invitation = db.query(Invitation).filter(
        Invitation.id == invitation_id,
        Invitation.invited_user_id == current_user.id,  # must be for this user
        Invitation.status == InvitationStatus.PENDING   # must still be pending
    ).first()

    if not invitation:
        raise HTTPException(404, "Pending invitation not found")

    # Update invitation status
    invitation.status = InvitationStatus.ACCEPTED
    invitation.responded_at = datetime.now(timezone.utc)

    # Add user to organization
    member = OrgMember(
        org_id=invitation.org_id,
        user_id=current_user.id
    )
    db.add(member)
    db.commit()  # both changes committed together

    return {"message": f"You have joined the organization"}


@invite_router.post("/{invitation_id}/decline", response_model=MessageResponse)
def decline_invitation(
    invitation_id: int,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    User declines an invitation.
    Status → DECLINED. No OrgMember row created.
    """
    invitation = db.query(Invitation).filter(
        Invitation.id == invitation_id,
        Invitation.invited_user_id == current_user.id,
        Invitation.status == InvitationStatus.PENDING
    ).first()

    if not invitation:
        raise HTTPException(404, "Pending invitation not found")

    invitation.status = InvitationStatus.DECLINED
    invitation.responded_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Invitation declined"}