"""Organization-related response models (Pydantic v2)."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class Organization(ModulexModel):
    """An organization record (nested in POST /organizations response)."""

    id: str
    name: Optional[str] = None
    slug: Optional[str] = None
    domain: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None


class OrganizationResponse(ModulexModel):
    """Response from POST /organizations (create)."""

    success: bool = True
    message: Optional[str] = None
    organization: Optional[Organization] = None


class LLMCatalogModel(ModulexModel):
    """A catalog LLM model entry inside the LLM list response.

    Backend merges catalog model fields with org/integration enrichment, so
    most fields are dynamic; only the enrichment keys are modeled explicitly.
    ``extra="allow"`` preserves the remaining catalog fields.
    """

    id: Optional[str] = None
    integration_name: Optional[str] = None
    integration_display_name: Optional[str] = None
    default_credential_display_name: Optional[str] = None


class LLMListResponse(ModulexModel):
    """Response from GET /organizations/llms."""

    success: bool = True
    total: int = 0
    active_llm_total: int = 0
    inactive_llm_total: int = 0
    active_llms: list[LLMCatalogModel] = Field(default_factory=list)
    inactive_llms: list[LLMCatalogModel] = Field(default_factory=list)


class InvitationDetail(ModulexModel):
    """The invitation sub-object returned by invite/reinvite."""

    id: str
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    token: Optional[str] = None
    expires_at: Optional[str] = None
    requires_acceptance: Optional[bool] = None


class InviteResponse(ModulexModel):
    """Response from POST /organizations/invite (and reinvite)."""

    success: bool = True
    message: Optional[str] = None
    invitation: Optional[InvitationDetail] = None
    error: Optional[str] = None
    code: Optional[str] = None


class RoleUpdateResponse(ModulexModel):
    """Response from PUT /organizations/{org}/users/{user}/role."""

    success: bool = True
    message: Optional[str] = None
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    new_role: Optional[str] = None


class InvitePreviewResponse(ModulexModel):
    """Response from POST /organizations/invite/preview (seat proration)."""

    preview_available: bool = False
    reason: Optional[str] = None
    interval: Optional[str] = None
    new_quantity: Optional[int] = None
    amount_due: Optional[float] = None
    currency: Optional[str] = None
    proration_line_amount: Optional[float] = None
    immediate: Optional[bool] = None


class VisibilityModel(ModulexModel):
    """A model entry inside the per-org LLM model visibility map."""

    id: str
    display_name: Optional[str] = None


class OrgComposerLLM(ModulexModel):
    """The organization's default composer LLM selection."""

    integration_name: Optional[str] = None
    provider_id: Optional[str] = None
    model_id: Optional[str] = None
    credential_id: Optional[str] = None


class OrgSettingsResponse(ModulexModel):
    """Response from GET /organizations/settings."""

    llm_model_visibility: dict[str, list[VisibilityModel]] = Field(default_factory=dict)
    composer_llm: Optional[OrgComposerLLM] = None


class LLMModelVisibilityResponse(ModulexModel):
    """Response from PUT /organizations/settings/llm-model-visibility."""

    llm_model_visibility: dict[str, list[VisibilityModel]] = Field(default_factory=dict)


class ComposerLLMResponse(ModulexModel):
    """Response from PUT /organizations/settings/composer-llm."""

    composer_llm: Optional[OrgComposerLLM] = None


class RemoveUserResponse(ModulexModel):
    """Response from DELETE /organizations/{org}/users/{user}."""

    success: bool = True
    message: Optional[str] = None


class CancelInvitationResponse(ModulexModel):
    """Response from POST /organizations/invitations/{id}/cancel."""

    success: bool = True
    message: Optional[str] = None
