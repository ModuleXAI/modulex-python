"""Integration tests for the Workflows resource.

Covers: list, create→get→update→delete lifecycle, builder_details.
"""

from __future__ import annotations

import pytest

from modulex import Modulex
from tests.integration.conftest import ResultTracker, api_call

_WORKFLOW_BODY = {
    "name": "SDK Integration Test Workflow",
    "description": "Created by integration tests — safe to delete",
    "workflow_schema": {
        "metadata": {"name": "test", "description": "test", "version": "1.0"},
        "nodes": [],
        "edges": [],
        "entry_point": "",
        "state_schema": {
            "fields": {
                "messages": {
                    "type": "messages",
                    "reducer": "add",
                    "required": True,
                }
            }
        },
        "config": {"recursion_limit": 25},
    },
    "status": "draft",
}


@pytest.mark.asyncio
class TestWorkflows:
    """Live API tests for workflow management endpoints."""

    async def test_list(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /workflows — response must contain 'workflows' and 'total' keys."""
        async with api_call(tracker, "GET", "/workflows") as call:
            result = await client.workflows.list()
            call.result = result
            assert isinstance(result, dict), f"list response must be a dict, got {type(result).__name__}"
            assert "workflows" in result, "'workflows' key missing from list response"
            assert "total" in result, "'total' key missing from list response"
            assert isinstance(result["workflows"], list), "'workflows' must be a list"
            assert isinstance(result["total"], int), "'total' must be an int"

    async def test_crud_lifecycle(self, client: Modulex, tracker: ResultTracker) -> None:
        """POST /workflows → GET /workflows/{id} → PUT /workflows/{id} → DELETE /workflows/{id}.

        Creates a minimal workflow, fetches it, updates its name, then deletes it.
        Deletion always runs in a finally block to avoid leaving orphaned resources.
        """
        created_id: str | None = None

        try:
            # --- CREATE ---
            async with api_call(tracker, "POST", "/workflows") as call:
                created = await client.workflows.create(
                    workflow_schema=_WORKFLOW_BODY["workflow_schema"],
                    name=_WORKFLOW_BODY["name"],
                    description=_WORKFLOW_BODY["description"],
                    status=_WORKFLOW_BODY["status"],
                )
                call.result = created
                assert isinstance(created, dict), f"create response must be a dict, got {type(created).__name__}"
                assert "id" in created, "'id' key missing from create response"
                created_id = created["id"]

            # --- GET ---
            async with api_call(tracker, "GET", f"/workflows/{created_id}") as call:
                fetched = await client.workflows.get(created_id)
                call.result = fetched
                assert isinstance(fetched, dict), f"get response must be a dict, got {type(fetched).__name__}"
                assert fetched.get("id") == created_id, (
                    f"get returned id={fetched.get('id')!r}, expected {created_id!r}"
                )

            # --- UPDATE ---
            updated_name = "SDK Integration Test Workflow (updated)"
            async with api_call(tracker, "PUT", f"/workflows/{created_id}") as call:
                updated = await client.workflows.update(created_id, name=updated_name)
                call.result = updated
                assert isinstance(updated, dict), f"update response must be a dict, got {type(updated).__name__}"
                assert updated.get("name") == updated_name, (
                    f"update returned name={updated.get('name')!r}, expected {updated_name!r}"
                )

        finally:
            if created_id:
                # --- DELETE ---
                async with api_call(tracker, "DELETE", f"/workflows/{created_id}") as call:
                    delete_result = await client.workflows.delete(created_id)
                    call.result = delete_result

    async def test_builder_details(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /workflows/builder/details — response must contain 'node_types' key."""
        async with api_call(tracker, "GET", "/workflows/builder/details") as call:
            result = await client.workflows.builder_details()
            call.result = result
            assert isinstance(result, dict), f"builder_details response must be a dict, got {type(result).__name__}"
            assert "node_types" in result, "'node_types' key missing from builder_details response"
            assert isinstance(result["node_types"], (list, dict)), "'node_types' must be a list or dict"
