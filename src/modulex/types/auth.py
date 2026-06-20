"""Auth-related response models (Pydantic v2)."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class UserProfile(ModulexModel):
    """User profile from GET /auth/me."""

    id: str
    email: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    is_active: bool = True
    organization_ids: list[str] = Field(default_factory=list)
    primary_organization_id: Optional[str] = None


class OrganizationMembership(ModulexModel):
    """An organization the user belongs to (GET /auth/me/organizations item)."""

    id: str
    name: Optional[str] = None
    slug: Optional[str] = None
    domain: Optional[str] = None
    role: Optional[str] = None
    joined_at: Optional[str] = None
    is_default: bool = False


class UserOrganizationsResponse(ModulexModel):
    """Response from GET /auth/me/organizations."""

    success: bool = True
    user_id: Optional[str] = None
    organizations: list[OrganizationMembership] = Field(default_factory=list)
    total: int = 0


class InvitationOrganization(ModulexModel):
    """Nested organization info inside an invitation."""

    id: str
    name: Optional[str] = None
    slug: Optional[str] = None
    domain: Optional[str] = None


class InvitedBy(ModulexModel):
    """The user who sent an invitation."""

    id: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None


class InvitationInfo(ModulexModel):
    """A pending invitation (GET /auth/invitations/my item)."""

    id: str
    organization: Optional[InvitationOrganization] = None
    invited_by: Optional[InvitedBy] = None
    role: Optional[str] = None
    status: Optional[str] = None
    invitation_message: Optional[str] = None
    days_until_expiry: Optional[int] = None
    created_at: Optional[str] = None
    expires_at: Optional[str] = None


class InvitationsResponse(ModulexModel):
    """Response from GET /auth/invitations/my."""

    success: bool = True
    invitations: list[InvitationInfo] = Field(default_factory=list)
    total_count: int = 0


class AcceptInvitationResponse(ModulexModel):
    """Response from POST /auth/invitations/{id}/accept."""

    success: bool = True
    message: Optional[str] = None
    organization: Optional[InvitationOrganization] = None
    role: Optional[str] = None


class RejectInvitationResponse(ModulexModel):
    """Response from POST /auth/invitations/{id}/reject."""

    success: bool = True
    message: Optional[str] = None


class LeaveOrganizationResponse(ModulexModel):
    """Response from POST /auth/organizations/leave."""

    success: bool = True
    message: Optional[str] = None
    left_organization: Optional[dict[str, Any]] = None
    remaining_organizations: list[OrganizationMembership] = Field(default_factory=list)
    total_remaining: int = 0
