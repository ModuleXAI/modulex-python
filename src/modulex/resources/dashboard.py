"""Dashboard resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource


class Dashboard(_BaseResource):
    """Resource for accessing dashboard logs, analytics, and user management."""

    async def logs(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        category: str | None = None,
        operation: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Return activity logs for the organization with optional filters."""
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "limit": limit,
                "offset": offset,
                "category": category,
                "operation": operation,
                "start_date": start_date,
                "end_date": end_date,
            }.items()
            if v is not None
        }
        return await self._get("/dashboard/logs", params=params, organization_id=organization_id)

    async def analytics_overview(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> Any:
        """Return a high-level analytics overview for the organization."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        return await self._get(
            "/dashboard/analytics/overview",
            params=params,
            organization_id=organization_id,
        )

    async def analytics_tools(
        self,
        *,
        period: str = "7d",
        limit: int = 20,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> Any:
        """Return tool usage analytics for the organization over a given period."""
        params: dict[str, Any] = {"period": period, "limit": limit, "offset": offset}
        return await self._get(
            "/dashboard/analytics/tools",
            params=params,
            organization_id=organization_id,
        )

    async def analytics_llm_usage(
        self,
        *,
        period: str = "7d",
        limit: int = 20,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> Any:
        """Return LLM token consumption analytics for the organization over a given period."""
        params: dict[str, Any] = {"period": period, "limit": limit, "offset": offset}
        return await self._get(
            "/dashboard/analytics/llm-usage",
            params=params,
            organization_id=organization_id,
        )

    async def users(
        self,
        *,
        search: str | None = None,
        status: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        page: int = 1,
        limit: int = 10,
        organization_id: str | None = None,
    ) -> Any:
        """Return paginated users for the organization with optional search and sort."""
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "search": search,
                "status": status,
                "sort_by": sort_by,
                "order": order,
                "page": page,
                "limit": limit,
            }.items()
            if v is not None
        }
        return await self._get("/dashboard/users", params=params, organization_id=organization_id)
