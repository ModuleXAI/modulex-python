"""API key-related response models (Pydantic v2)."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class ApiKeyResponse(ModulexModel):
    """A single API key (GET /api-keys/{key_id} and list item).

    Raw key is never returned here; only ``masked_key``/``key_hint``.
    """

    id: str
    name: Optional[str] = None
    key_hint: Optional[str] = None
    masked_key: Optional[str] = None
    organization_id: Optional[str] = None
    expires_at: Optional[str] = None
    is_expired: bool = False
    is_active: bool = True
    rate_limit_per_minute: int = 60
    last_used_at: Optional[str] = None
    created_at: Optional[str] = None
    revoked_at: Optional[str] = None


class CreateApiKeyResponse(ModulexModel):
    """Response from POST /api-keys.

    The raw ``key`` is returned ONLY here, exactly once, and can never be
    retrieved again.
    """

    id: str
    name: Optional[str] = None
    key: Optional[str] = None
    key_hint: Optional[str] = None
    masked_key: Optional[str] = None
    organization_id: Optional[str] = None
    expires_at: Optional[str] = None
    is_expired: bool = False
    is_active: bool = True
    rate_limit_per_minute: int = 60
    last_used_at: Optional[str] = None
    created_at: Optional[str] = None
    revoked_at: Optional[str] = None


class ApiKeyListResponse(ModulexModel):
    """Response envelope from GET /api-keys."""

    keys: list[ApiKeyResponse] = Field(default_factory=list)
    total: int = 0
    max_keys: int = 0


class RevokeApiKeyResponse(ModulexModel):
    """Response from DELETE /api-keys/{key_id}."""

    success: bool = True
    message: Optional[str] = None
