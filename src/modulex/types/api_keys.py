"""API key-related type definitions."""

from __future__ import annotations

from typing_extensions import TypedDict


class ApiKeyResponse(TypedDict, total=False):
    """Response representing an API key."""

    id: str
    name: str
    key: str | None
    key_hint: str
    organization_id: str
    expires_at: str | None
    rate_limit_per_minute: int | None
    created_at: str
    is_revoked: bool
