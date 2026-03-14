"""Auth resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource


class Auth(_BaseResource):
    """Resource for authentication and identity endpoints."""

    async def me(self) -> Any:
        """Return the currently authenticated user's profile."""
        return await self._get("/auth/me")

    async def organizations(self, *, role: str | None = None) -> Any:
        """Return organizations the current user belongs to, optionally filtered by role."""
        params: dict[str, Any] = {}
        if role is not None:
            params["role"] = role
        return await self._get("/auth/me/organizations", params=params or None)

    async def invitations(self) -> Any:
        """Return all pending invitations for the current user."""
        return await self._get("/auth/invitations/my")

    async def accept_invitation(self, invitation_id: str) -> Any:
        """Accept a pending organization invitation by its ID."""
        return await self._post(f"/auth/invitations/{invitation_id}/accept")

    async def reject_invitation(self, invitation_id: str) -> Any:
        """Reject a pending organization invitation by its ID."""
        return await self._post(f"/auth/invitations/{invitation_id}/reject")

    async def leave_organization(self, *, organization_id: str | None = None) -> Any:
        """Leave the organization identified by the organization_id header."""
        return await self._post("/auth/organizations/leave", organization_id=organization_id)
