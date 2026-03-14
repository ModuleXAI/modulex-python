"""Auth-related type definitions."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class UserProfile(TypedDict, total=False):
    """User profile from /auth/me."""

    id: str
    email: str
    username: str
    role: str
    is_active: bool
    organization_ids: list[str]
    primary_organization_id: str | None


class OrganizationMembership(TypedDict, total=False):
    """Organization membership info."""

    id: str
    name: str
    slug: str
    role: str
    created_at: str


class UserOrganizationsResponse(TypedDict, total=False):
    """Response from /auth/me/organizations."""

    success: bool
    user_id: str
    organizations: list[OrganizationMembership]
    total: int


class InvitationInfo(TypedDict, total=False):
    """Invitation details."""

    id: str
    organization_id: str
    organization_name: str
    invited_email: str
    role: str
    status: str
    invitation_message: str | None
    created_at: str
    expires_at: str | None


class LeaveOrganizationResponse(TypedDict, total=False):
    """Response from /auth/organizations/leave."""

    success: bool
    message: str
    left_organization: dict[str, Any]
    remaining_organizations: list[dict[str, Any]]
    total_remaining: int
