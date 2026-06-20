"""System resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource
from modulex.types.system import (
    SystemHealthResponse,
    TimezoneListResponse,
    TimezoneOption,
)


class System(_BaseResource):
    """Resource for system-level health and reference data."""

    async def health(self) -> SystemHealthResponse:
        """Return the current health status of the API service."""
        return SystemHealthResponse.model_validate(await self._get("/system/health"))

    async def timezones(self) -> TimezoneListResponse:
        """Return the full list of supported IANA timezone identifiers."""
        return TimezoneListResponse.model_validate(await self._get("/system/timezones"))

    async def search_timezones(self, query: str) -> list[TimezoneOption]:
        """Search supported timezones by a keyword query string."""
        params: dict[str, Any] = {"q": query}
        result = await self._get("/system/timezones/search", params=params)
        return [TimezoneOption.model_validate(item) for item in (result or [])]
