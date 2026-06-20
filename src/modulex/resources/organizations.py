"""Organizations resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any, Literal

from modulex._base import _BaseResource
from modulex.types.organizations import (
    CancelInvitationResponse,
    ComposerLLMResponse,
    InvitePreviewResponse,
    InviteResponse,
    LLMListResponse,
    LLMModelVisibilityResponse,
    OrganizationResponse,
    OrgSettingsResponse,
    RemoveUserResponse,
    RoleUpdateResponse,
)


class Organizations(_BaseResource):
    """Resource for managing organizations and their memberships."""

    async def create(self, name: str, *, slug: str | None = None) -> OrganizationResponse:
        """Create a new organization with the given name and optional slug."""
        body: dict[str, Any] = {"name": name}
        if slug is not None:
            body["slug"] = slug
        return OrganizationResponse.model_validate(await self._post("/organizations", json=body))

    async def llms(self, *, organization_id: str | None = None) -> LLMListResponse:
        """Return the LLM configurations available to the organization."""
        return LLMListResponse.model_validate(await self._get("/organizations/llms", organization_id=organization_id))

    async def invite(
        self,
        invited_email: str,
        *,
        role: Literal["admin"] = "admin",
        invitation_message: str | None = None,
        organization_id: str | None = None,
    ) -> InviteResponse:
        """Send an invitation email to a user to join the organization.

        Orgs are owner/admin only: the creator is ``owner`` and every invited user
        is ``admin``. ``role`` must be ``"admin"`` (the default) — the ``"member"``
        role has been retired and the backend rejects it with HTTP 422.
        """
        body: dict[str, Any] = {"invited_email": invited_email, "role": role}
        if invitation_message is not None:
            body["invitation_message"] = invitation_message
        return InviteResponse.model_validate(
            await self._post("/organizations/invite", json=body, organization_id=organization_id)
        )

    async def preview_invite(self, *, organization_id: str | None = None) -> InvitePreviewResponse:
        """Preview the prorated cost of adding one seat before sending an invite.

        Returns {preview_available: False, reason} on a free plan, otherwise
        {preview_available: True, interval, new_quantity, amount_due, currency,
        proration_line_amount, immediate}. Requires admin/owner.
        """
        return InvitePreviewResponse.model_validate(
            await self._post("/organizations/invite/preview", organization_id=organization_id)
        )

    async def get_settings(self, *, organization_id: str | None = None) -> OrgSettingsResponse:
        """Return per-org LLM preferences ({llm_model_visibility, composer_llm})."""
        return OrgSettingsResponse.model_validate(
            await self._get("/organizations/settings", organization_id=organization_id)
        )

    async def set_llm_model_visibility(
        self,
        integration_name: str,
        models: list[dict[str, Any]],
        *,
        organization_id: str | None = None,
    ) -> LLMModelVisibilityResponse:
        """Set the visible model list for an integration (empty list resets to default).

        Each model entry is {id, display_name?}. Requires admin/owner.
        """
        return LLMModelVisibilityResponse.model_validate(
            await self._put(
                "/organizations/settings/llm-model-visibility",
                json={"integration_name": integration_name, "models": models},
                organization_id=organization_id,
            )
        )

    async def set_composer_llm(
        self,
        integration_name: str,
        provider_id: str,
        model_id: str,
        *,
        credential_id: str | None = None,
        organization_id: str | None = None,
    ) -> ComposerLLMResponse:
        """Set the organization's default composer/assistant LLM. Requires admin/owner."""
        body: dict[str, Any] = {
            "integration_name": integration_name,
            "provider_id": provider_id,
            "model_id": model_id,
        }
        if credential_id is not None:
            body["credential_id"] = credential_id
        return ComposerLLMResponse.model_validate(
            await self._put(
                "/organizations/settings/composer-llm",
                json=body,
                organization_id=organization_id,
            )
        )

    async def cancel_invitation(
        self, invitation_id: str, *, organization_id: str | None = None
    ) -> CancelInvitationResponse:
        """Cancel a pending organization invitation by its ID."""
        return CancelInvitationResponse.model_validate(
            await self._post(
                f"/organizations/invitations/{invitation_id}/cancel",
                organization_id=organization_id,
            )
        )

    async def reinvite(self, invitation_id: str, *, organization_id: str | None = None) -> InviteResponse:
        """Resend an organization invitation by its ID."""
        return InviteResponse.model_validate(
            await self._post(
                f"/organizations/invitations/{invitation_id}/reinvite",
                organization_id=organization_id,
            )
        )

    async def update_user_role(
        self,
        org_id: str,
        user_id: str,
        role: Literal["admin"],
        *,
        organization_id: str | None = None,
    ) -> RoleUpdateResponse:
        """Update the role of a user within an organization.

        ``role`` must be ``"admin"`` — the ``"member"`` role has been retired (orgs
        are owner/admin only) and the backend rejects it with HTTP 422.
        """
        return RoleUpdateResponse.model_validate(
            await self._put(
                f"/organizations/{org_id}/users/{user_id}/role",
                json={"role": role},
                organization_id=organization_id,
            )
        )

    async def remove_user(self, org_id: str, user_id: str, *, organization_id: str | None = None) -> RemoveUserResponse:
        """Remove a user from an organization."""
        return RemoveUserResponse.model_validate(
            await self._delete(
                f"/organizations/{org_id}/users/{user_id}",
                organization_id=organization_id,
            )
        )
