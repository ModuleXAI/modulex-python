"""Tests for the Workflows resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from modulex import Modulex


@pytest.mark.asyncio
class TestWorkflows:
    async def test_list(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/workflows").mock(
            return_value=httpx.Response(
                200,
                json={
                    "workflows": [{"id": "wf-1", "name": "Test WF"}],
                    "total": 1,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 1,
                },
            )
        )
        result = await client.workflows.list(status="active", page=1, page_size=20)
        assert result["total"] == 1
        assert result["workflows"][0]["name"] == "Test WF"

    async def test_list_query_params(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.get("/workflows").mock(
            return_value=httpx.Response(
                200,
                json={
                    "workflows": [],
                    "total": 0,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 0,
                },
            )
        )
        await client.workflows.list(status="active", search="email", category="automation")
        params = dict(route.calls.last.request.url.params)
        assert params["status"] == "active"
        assert params["search"] == "email"
        assert params["category"] == "automation"

    async def test_get(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/workflows/wf-123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "wf-123",
                    "name": "My Workflow",
                    "workflow_schema": {"nodes": [], "edges": []},
                },
            )
        )
        result = await client.workflows.get("wf-123")
        assert result["id"] == "wf-123"
        assert "workflow_schema" in result

    async def test_create(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/workflows").mock(
            return_value=httpx.Response(
                201,
                json={
                    "id": "wf-new",
                    "name": "New Workflow",
                    "status": "draft",
                },
            )
        )
        result = await client.workflows.create(
            workflow_schema={"nodes": [], "edges": [], "entry_point": "start"},
            name="New Workflow",
            status="draft",
        )
        assert result["id"] == "wf-new"

    async def test_update(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.put("/workflows/wf-123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "wf-123",
                    "name": "Updated",
                    "status": "active",
                },
            )
        )
        result = await client.workflows.update("wf-123", name="Updated", status="active")
        assert result["name"] == "Updated"

    async def test_delete(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.delete("/workflows/wf-123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "deleted",
                    "workflow_id": "wf-123",
                    "message": "Workflow deleted",
                },
            )
        )
        result = await client.workflows.delete("wf-123")
        assert result["status"] == "deleted"

    async def test_builder_details(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/workflows/builder/details").mock(
            return_value=httpx.Response(
                200,
                json={
                    "node_types": {},
                    "categories": {},
                    "counts": {},
                    "cached": True,
                },
            )
        )
        result = await client.workflows.builder_details(node_type="llm")
        assert result["cached"] is True

    async def test_list_all_autopagination(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/workflows").mock(
            side_effect=[
                httpx.Response(
                    200,
                    json={
                        "workflows": [{"id": "wf-1"}, {"id": "wf-2"}],
                        "total": 4,
                        "page": 1,
                        "page_size": 2,
                        "total_pages": 2,
                    },
                ),
                httpx.Response(
                    200,
                    json={
                        "workflows": [{"id": "wf-3"}, {"id": "wf-4"}],
                        "total": 4,
                        "page": 2,
                        "page_size": 2,
                        "total_pages": 2,
                    },
                ),
            ]
        )
        items = []
        async for wf in client.workflows.list_all():
            items.append(wf)
        assert len(items) == 4
        assert items[0]["id"] == "wf-1"
        assert items[3]["id"] == "wf-4"

    async def test_org_id_override(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.get("/workflows").mock(
            return_value=httpx.Response(
                200,
                json={
                    "workflows": [],
                    "total": 0,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 0,
                },
            )
        )
        await client.workflows.list(organization_id="override-org")
        assert route.calls.last.request.headers["X-Organization-ID"] == "override-org"
