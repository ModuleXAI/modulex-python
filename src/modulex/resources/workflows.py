"""Workflows resource for the ModuleX Python SDK."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from modulex._base import _BaseResource
from modulex._streaming import EventSourceStream


class Workflows(_BaseResource):
    """Resource for creating and managing workflow definitions."""

    async def create(
        self,
        workflow_schema: dict[str, Any],
        *,
        name: str | None = None,
        description: str | None = None,
        version: str | None = None,
        tags: list[str] | None = None,
        category: str | None = None,
        status: str = "draft",
        visibility: str = "private",
        input: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Create a new workflow from the given schema and metadata."""
        body: dict[str, Any] = {
            "workflow_schema": workflow_schema,
            "status": status,
            "visibility": visibility,
        }
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if version is not None:
            body["version"] = version
        if tags is not None:
            body["tags"] = tags
        if category is not None:
            body["category"] = category
        if input is not None:
            body["input"] = input
        if config is not None:
            body["config"] = config
        return await self._post("/workflows", json=body, organization_id=organization_id)

    async def list(
        self,
        *,
        status: str | None = None,
        category: str | None = None,
        visibility: str | None = None,
        search: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Return a paginated list of workflows matching the given filters."""
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if category is not None:
            params["category"] = category
        if visibility is not None:
            params["visibility"] = visibility
        if search is not None:
            params["search"] = search
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        return await self._get("/workflows", params=params or None, organization_id=organization_id)

    async def list_all(
        self,
        *,
        status: str | None = None,
        category: str | None = None,
        visibility: str | None = None,
        search: str | None = None,
        organization_id: str | None = None,
    ) -> AsyncIterator[Any]:
        """Auto-paginate through all workflows matching the given filters."""
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if category is not None:
            params["category"] = category
        if visibility is not None:
            params["visibility"] = visibility
        if search is not None:
            params["search"] = search
        params["page"] = 1
        async for item in self._paginate(
            "/workflows",
            items_key="workflows",
            params=params,
            organization_id=organization_id,
        ):
            yield item

    async def get(self, workflow_id: str, *, organization_id: str | None = None) -> Any:
        """Return a single workflow by its ID."""
        return await self._get(f"/workflows/{workflow_id}", organization_id=organization_id)

    async def update(self, workflow_id: str, *, organization_id: str | None = None, **kwargs: Any) -> Any:
        """Update a workflow's fields with any combination of allowed keys."""
        allowed_keys = {
            "name",
            "description",
            "version",
            "tags",
            "category",
            "status",
            "visibility",
            "workflow_schema",
            "input",
            "config",
        }
        body = {k: v for k, v in kwargs.items() if k in allowed_keys and v is not None}
        return await self._put(f"/workflows/{workflow_id}", json=body, organization_id=organization_id)

    async def delete(self, workflow_id: str, *, organization_id: str | None = None) -> Any:
        """Delete a workflow by its ID."""
        return await self._delete(f"/workflows/{workflow_id}", organization_id=organization_id)

    async def builder_details(
        self,
        *,
        node_type: str | None = None,
        category: str | None = None,
        integration_name: str | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Return workflow builder node details, optionally filtered by type, category, or integration."""
        params: dict[str, Any] = {}
        if node_type is not None:
            params["node_type"] = node_type
        if category is not None:
            params["category"] = category
        if integration_name is not None:
            params["integration_name"] = integration_name
        return await self._get(
            "/workflows/builder/details",
            params=params or None,
            organization_id=organization_id,
        )

    def listen_changes(self, workflow_id: str, *, organization_id: str | None = None) -> EventSourceStream:
        """Open an SSE stream for live changes to a workflow definition."""
        return self._stream_sse(f"/workflows/{workflow_id}/changes", organization_id=organization_id)
