"""Auth resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource
from modulex.types.auth import (
    AcceptInvitationResponse,
    InvitationsResponse,
    LeaveOrganizationResponse,
    RejectInvitationResponse,
    UserOrganizationsResponse,
    UserProfile,
)


class Auth(_BaseResource):
    """Resource for authentication and identity endpoints."""

    async def me(self) -> UserProfile:
        """Return the currently authenticated user's profile."""
        return UserProfile.model_validate(await self._get("/auth/me"))

    async def organizations(self, *, role: str | None = None) -> UserOrganizationsResponse:
        """Return organizations the current user belongs to, optionally filtered by role."""
        params: dict[str, Any] = {}
        if role is not None:
            params["role"] = role
        return UserOrganizationsResponse.model_validate(
            await self._get("/auth/me/organizations", params=params or None)
        )

    async def invitations(self) -> InvitationsResponse:
        """Return all pending invitations for the current user."""
        return InvitationsResponse.model_validate(await self._get("/auth/invitations/my"))

    async def accept_invitation(self, invitation_id: str) -> AcceptInvitationResponse:
        """Accept a pending organization invitation by its ID."""
        return AcceptInvitationResponse.model_validate(await self._post(f"/auth/invitations/{invitation_id}/accept"))

    async def reject_invitation(self, invitation_id: str) -> RejectInvitationResponse:
        """Reject a pending organization invitation by its ID."""
        return RejectInvitationResponse.model_validate(await self._post(f"/auth/invitations/{invitation_id}/reject"))

    async def leave_organization(self, *, organization_id: str | None = None) -> LeaveOrganizationResponse:
        """Leave the organization identified by the organization_id header."""
        return LeaveOrganizationResponse.model_validate(
            await self._post("/auth/organizations/leave", organization_id=organization_id)
        )
