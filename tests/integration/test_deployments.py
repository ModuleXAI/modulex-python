"""Integration tests for the Deployments resource.

Covers full lifecycle: create → list → get → activate → deactivate → delete.

All tests in this module are skipped when MODULEX_TEST_WORKFLOW_ID is not set
because deployments are anchored to a specific workflow.
"""

from __future__ import annotations

import pytest

from modulex import Modulex
from tests.integration.conftest import ResultTracker, api_call, skip_call


@pytest.mark.asyncio
class TestDeployments:
    """Live API tests for workflow deployment endpoints."""

    async def test_lifecycle(
        self,
        client: Modulex,
        tracker: ResultTracker,
        test_workflow_id: str,
    ) -> None:
        """POST deploy → GET list → GET by ID → PUT activate → DELETE live → DELETE deployment.

        Runs the full deployment lifecycle against test_workflow_id. Cleanup always
        runs in a finally block to avoid leaving orphaned deployments.
        """
        if not test_workflow_id:
            skip_call(
                tracker,
                "POST",
                f"/workflows/{test_workflow_id or '<id>'}/deploy",
                "MODULEX_TEST_WORKFLOW_ID not set",
            )
            for method, path in [
                ("GET", f"/workflows/{test_workflow_id or '<id>'}/deployments"),
                ("GET", f"/workflows/{test_workflow_id or '<id>'}/deployments/<dep_id>"),
                ("PUT", f"/workflows/{test_workflow_id or '<id>'}/deployments/<dep_id>/activate"),
                ("DELETE", f"/workflows/{test_workflow_id or '<id>'}/deployments/live"),
                ("DELETE", f"/workflows/{test_workflow_id or '<id>'}/deployments/<dep_id>"),
            ]:
                skip_call(tracker, method, path, "MODULEX_TEST_WORKFLOW_ID not set")
            pytest.skip("MODULEX_TEST_WORKFLOW_ID not set")

        wf_id = test_workflow_id
        deployment_id: str | None = None

        try:
            # --- CREATE (deploy) ---
            async with api_call(tracker, "POST", f"/workflows/{wf_id}/deploy") as call:
                created = await client.deployments.create(
                    wf_id,
                    deployment_note="SDK integration test deployment — safe to delete",
                )
                call.result = created
                assert isinstance(created, dict), f"deploy response must be a dict, got {type(created).__name__}"
                assert "id" in created, "'id' key missing from deploy response"
                deployment_id = created["id"]

            # --- LIST ---
            async with api_call(tracker, "GET", f"/workflows/{wf_id}/deployments") as call:
                listing = await client.deployments.list(wf_id)
                call.result = listing
                # Response may be a list or a dict wrapping a list.
                if isinstance(listing, list):
                    dep_ids = [d.get("id") for d in listing if isinstance(d, dict)]
                else:
                    assert isinstance(listing, dict), (
                        f"list response must be a list or dict, got {type(listing).__name__}"
                    )
                    items = listing.get("deployments") or listing.get("data") or []
                    dep_ids = [d.get("id") for d in items if isinstance(d, dict)]

                assert deployment_id in dep_ids, f"new deployment {deployment_id!r} not found in list response"

            # --- GET BY ID ---
            async with api_call(tracker, "GET", f"/workflows/{wf_id}/deployments/{deployment_id}") as call:
                fetched = await client.deployments.get(wf_id, deployment_id)
                call.result = fetched
                assert isinstance(fetched, dict), f"get response must be a dict, got {type(fetched).__name__}"
                assert fetched.get("id") == deployment_id, (
                    f"get returned id={fetched.get('id')!r}, expected {deployment_id!r}"
                )

            # --- ACTIVATE ---
            async with api_call(tracker, "PUT", f"/workflows/{wf_id}/deployments/{deployment_id}/activate") as call:
                activated = await client.deployments.activate(wf_id, deployment_id)
                call.result = activated
                assert activated is not None, "activate response must not be None"

            # --- DEACTIVATE (delete live) ---
            async with api_call(tracker, "DELETE", f"/workflows/{wf_id}/deployments/live") as call:
                deactivated = await client.deployments.deactivate(wf_id)
                call.result = deactivated
                assert deactivated is not None, "deactivate response must not be None"

        finally:
            if deployment_id:
                # --- DELETE deployment record ---
                async with api_call(tracker, "DELETE", f"/workflows/{wf_id}/deployments/{deployment_id}") as call:
                    delete_result = await client.deployments.delete(wf_id, deployment_id)
                    call.result = delete_result

            # Re-deploy so later tests (executions, schedules) find an active deployment.
            restored = await client.deployments.create(
                wf_id,
                deployment_note="Restored by integration test suite",
            )
            restored_id = restored.get("id", "")
            if restored_id:
                await client.deployments.activate(wf_id, restored_id)
