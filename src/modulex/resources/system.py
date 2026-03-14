"""System resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource


class System(_BaseResource):
    """Resource for system-level health, metrics, and reference data."""

    async def health(self) -> Any:
        """Return the current health status of the API service."""
        return await self._get("/system/health")

    async def metrics(self) -> Any:
        """Return system-level performance and usage metrics."""
        return await self._get("/system/metrics")

    async def timezones(self) -> Any:
        """Return the full list of supported IANA timezone identifiers."""
        return await self._get("/system/timezones")

    async def search_timezones(self, query: str) -> Any:
        """Search supported timezones by a keyword query string."""
        params: dict[str, Any] = {"q": query}
        return await self._get("/system/timezones/search", params=params)
