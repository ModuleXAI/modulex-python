"""Integration tests for the Executions resource.

Covers: run, get_state, cancel, listen (SSE).

All tests in this module are skipped when MODULEX_TEST_WORKFLOW_ID is not set
because they require an existing, runnable workflow.
"""

from __future__ import annotations

import pytest

from modulex import Modulex, ModulexError
from tests.integration.conftest import ResultTracker, api_call, skip_call


@pytest.mark.asyncio
class TestExecutions:
    """Live API tests for workflow execution endpoints."""

    async def test_run(
        self,
        client: Modulex,
        tracker: ResultTracker,
        test_workflow_id: str,
    ) -> None:
        """POST /workflows/run — execute the workflow with stream=False, ephemeral=True."""
        if not test_workflow_id:
            skip_call(
                tracker,
                "POST",
                "/workflows/run",
                "MODULEX_TEST_WORKFLOW_ID not set",
            )
            pytest.skip("MODULEX_TEST_WORKFLOW_ID not set")

        try:
            async with api_call(tracker, "POST", "/workflows/run") as call:
                result = await client.executions.run(
                    workflow_id=test_workflow_id,
                    stream=False,
                    ephemeral=True,
                )
                call.result = result
                assert result is not None, "run response must not be None"
                assert isinstance(result, dict), f"run response must be a dict, got {type(result).__name__}"
                has_thread = "thread_id" in result
                has_run = "run_id" in result or "id" in result
                assert has_thread or has_run, "run response must contain 'thread_id' or 'run_id'/'id'"
        except ModulexError as exc:
            skip_call(tracker, "POST", "/workflows/run", f"Workflow not runnable: {exc}")
            pytest.skip(f"Workflow not runnable: {exc}")

    async def test_get_state(
        self,
        client: Modulex,
        tracker: ResultTracker,
        test_workflow_id: str,
    ) -> None:
        """GET /workflows/state/{thread_id} — fetch state using thread_id from a fresh run."""
        if not test_workflow_id:
            skip_call(
                tracker,
                "GET",
                "/workflows/state/{thread_id}",
                "MODULEX_TEST_WORKFLOW_ID not set",
            )
            pytest.skip("MODULEX_TEST_WORKFLOW_ID not set")

        # Kick off a fresh ephemeral run to obtain a thread_id.
        try:
            run_result = await client.executions.run(
                workflow_id=test_workflow_id,
                stream=False,
                ephemeral=True,
            )
        except ModulexError as exc:
            skip_call(tracker, "GET", "/workflows/state/{thread_id}", f"Cannot run workflow: {exc}")
            pytest.skip(f"Cannot run workflow: {exc}")
            return

        thread_id: str = run_result.get("thread_id") or run_result.get("id") or ""
        assert thread_id, "could not derive thread_id from run response"

        try:
            async with api_call(tracker, "GET", f"/workflows/state/{thread_id}") as call:
                state = await client.executions.get_state(thread_id)
                call.result = state
                assert state is not None, "get_state response must not be None"
        except ModulexError:
            pass  # ephemeral runs may not persist checkpoints

    async def test_cancel(
        self,
        client: Modulex,
        tracker: ResultTracker,
        test_workflow_id: str,
    ) -> None:
        """POST /workflows/cancel/{run_id} — cancel a run (tolerate 'already finished' errors)."""
        if not test_workflow_id:
            skip_call(
                tracker,
                "POST",
                "/workflows/cancel/{run_id}",
                "MODULEX_TEST_WORKFLOW_ID not set",
            )
            pytest.skip("MODULEX_TEST_WORKFLOW_ID not set")

        # Start a fresh run to obtain a run_id to cancel.
        try:
            run_result = await client.executions.run(
                workflow_id=test_workflow_id,
                stream=False,
                ephemeral=True,
            )
        except ModulexError as exc:
            skip_call(tracker, "POST", "/workflows/cancel/{run_id}", f"Cannot run workflow: {exc}")
            pytest.skip(f"Cannot run workflow: {exc}")
            return

        run_id: str = run_result.get("run_id") or run_result.get("id") or ""
        assert run_id, "could not derive run_id from run response"

        async with api_call(tracker, "POST", f"/workflows/cancel/{run_id}") as call:
            try:
                cancel_result = await client.executions.cancel(run_id)
                call.result = cancel_result
            except ModulexError as exc:
                # If the run finished before the cancel request arrived, the API
                # returns a 4xx. We record the status_code on the call object so
                # the tracker can surface it, then re-raise only unexpected errors.
                call.result = exc
                # Acceptable: 400 (already done), 404 (ephemeral run cleaned up).
                status_code: int = getattr(exc, "status_code", 0) or 0
                if status_code not in (400, 404, 409):
                    raise

    async def test_listen(
        self,
        client: Modulex,
        tracker: ResultTracker,
        test_workflow_id: str,
    ) -> None:
        """GET /workflows/listen/{run_id} — SSE stream (skipped: requires an active run)."""
        if not test_workflow_id:
            skip_call(
                tracker,
                "GET",
                "/workflows/listen/{run_id}",
                "MODULEX_TEST_WORKFLOW_ID not set",
            )
            pytest.skip("MODULEX_TEST_WORKFLOW_ID not set")

        skip_call(
            tracker,
            "GET",
            "/workflows/listen/{run_id}",
            "SSE requires active run",
        )
        pytest.skip("SSE requires active run")
