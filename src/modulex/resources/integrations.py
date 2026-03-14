"""Integrations resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource


class Integrations(_BaseResource):
    """Resource for browsing and inspecting available integrations."""

    async def browse(
        self,
        *,
        category: str | None = None,
        type: str | None = None,
        auth_type: str | None = None,
        search: str | None = None,
        include_details: bool = True,
        paginate: bool = True,
        page: int = 1,
        page_size: int = 50,
        organization_id: str | None = None,
    ) -> Any:
        """Browse all available integrations with optional filters and pagination."""
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "category": category,
                "type": type,
                "auth_type": auth_type,
                "search": search,
                "include_details": include_details,
                "paginate": paginate,
                "page": page,
                "page_size": page_size,
            }.items()
            if v is not None
        }
        return await self._get("/integrations/browse", params=params, organization_id=organization_id)

    async def tools(
        self,
        *,
        category: str | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Return available tool integrations, optionally filtered by category."""
        params: dict[str, Any] = {k: v for k, v in {"category": category}.items() if v is not None}
        return await self._get("/integrations/tools", params=params, organization_id=organization_id)

    async def tool_detail(
        self,
        integration_name: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Return detailed information for a single tool integration by name."""
        return await self._get(f"/integrations/tools/{integration_name}", organization_id=organization_id)

    async def llm_providers(
        self,
        *,
        category: str | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Return available LLM provider integrations, optionally filtered by category."""
        params: dict[str, Any] = {k: v for k, v in {"category": category}.items() if v is not None}
        return await self._get("/integrations/llm-providers", params=params, organization_id=organization_id)

    async def llm_provider_detail(
        self,
        provider_name: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Return detailed information for a single LLM provider by name."""
        return await self._get(f"/integrations/llm-providers/{provider_name}", organization_id=organization_id)

    async def knowledge_providers(
        self,
        *,
        category: str | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Return available knowledge provider integrations, optionally filtered by category."""
        params: dict[str, Any] = {k: v for k, v in {"category": category}.items() if v is not None}
        return await self._get("/integrations/knowledge-providers", params=params, organization_id=organization_id)

    async def knowledge_provider_detail(
        self,
        provider_name: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Return detailed information for a single knowledge provider by name."""
        return await self._get(
            f"/integrations/knowledge-providers/{provider_name}",
            organization_id=organization_id,
        )

    async def get(
        self,
        integration_name: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Return the integration record for a given integration name."""
        return await self._get(f"/integrations/{integration_name}", organization_id=organization_id)
