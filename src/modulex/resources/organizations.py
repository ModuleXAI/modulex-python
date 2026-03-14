"""Organizations resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource


class Organizations(_BaseResource):
    """Resource for managing organizations and their memberships."""

    async def create(self, name: str, *, slug: str | None = None) -> Any:
        """Create a new organization with the given name and optional slug."""
        body: dict[str, Any] = {"name": name}
        if slug is not None:
            body["slug"] = slug
        return await self._post("/organizations", json=body)

    async def llms(self, *, organization_id: str | None = None) -> Any:
        """Return the LLM configurations available to the organization."""
        return await self._get("/organizations/llms", organization_id=organization_id)

    async def invite(
        self,
        invited_email: str,
        *,
        role: str = "member",
        invitation_message: str | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Send an invitation email to a user to join the organization."""
        body: dict[str, Any] = {"invited_email": invited_email, "role": role}
        if invitation_message is not None:
            body["invitation_message"] = invitation_message
        return await self._post("/organizations/invite", json=body, organization_id=organization_id)

    async def cancel_invitation(self, invitation_id: str, *, organization_id: str | None = None) -> Any:
        """Cancel a pending organization invitation by its ID."""
        return await self._post(
            f"/organizations/invitations/{invitation_id}/cancel",
            organization_id=organization_id,
        )

    async def reinvite(self, invitation_id: str, *, organization_id: str | None = None) -> Any:
        """Resend an organization invitation by its ID."""
        return await self._post(
            f"/organizations/invitations/{invitation_id}/reinvite",
            organization_id=organization_id,
        )

    async def update_user_role(
        self,
        org_id: str,
        user_id: str,
        role: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Update the role of a user within an organization."""
        return await self._put(
            f"/organizations/{org_id}/users/{user_id}/role",
            json={"role": role},
            organization_id=organization_id,
        )

    async def remove_user(self, org_id: str, user_id: str, *, organization_id: str | None = None) -> Any:
        """Remove a user from an organization."""
        return await self._delete(
            f"/organizations/{org_id}/users/{user_id}",
            organization_id=organization_id,
        )
