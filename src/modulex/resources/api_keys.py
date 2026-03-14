"""ApiKeys resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource


class ApiKeys(_BaseResource):
    """Resource for managing API keys."""

    async def create(
        self,
        name: str,
        *,
        organization_id: str | None = None,
        expires_at: str | None = None,
        rate_limit_per_minute: int = 60,
    ) -> Any:
        """Create a new API key with the given name and options."""
        body: dict[str, Any] = {"name": name, "rate_limit_per_minute": rate_limit_per_minute}
        if organization_id is not None:
            body["organization_id"] = organization_id
        if expires_at is not None:
            body["expires_at"] = expires_at
        return await self._post("/api-keys", json=body)

    async def list(self, *, include_revoked: bool = False) -> Any:
        """Return all API keys, optionally including revoked ones."""
        return await self._get("/api-keys", params={"include_revoked": include_revoked})

    async def get(self, key_id: str) -> Any:
        """Return a single API key by its ID."""
        return await self._get(f"/api-keys/{key_id}")

    async def revoke(self, key_id: str) -> Any:
        """Revoke an API key by its ID."""
        return await self._delete(f"/api-keys/{key_id}")
