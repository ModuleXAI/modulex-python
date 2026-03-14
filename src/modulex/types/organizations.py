"""Organization-related type definitions."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class OrganizationResponse(TypedDict, total=False):
    """Generic organization action response."""

    success: bool
    message: str
    organization: dict[str, Any]


class LLMListResponse(TypedDict, total=False):
    """Response listing LLM configurations for an organization."""

    success: bool
    total: int
    active_llm_total: int
    inactive_llm_total: int
    active_llms: list[Any]
    inactive_llms: list[Any]


class InviteResponse(TypedDict, total=False):
    """Response from sending an organization invitation."""

    success: bool
    message: str


class RoleUpdateResponse(TypedDict, total=False):
    """Response from updating a member's role."""

    success: bool
    message: str
    user_id: str
    organization_id: str
    new_role: str
