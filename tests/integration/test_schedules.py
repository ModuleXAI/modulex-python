from __future__ import annotations

import pytest

from modulex import Modulex, ModulexError
from tests.integration.conftest import ResultTracker, api_call, skip_call


@pytest.mark.asyncio
class TestSchedules:
    """Integration tests for the /schedules endpoints."""

    async def test_list(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /schedules — response is a list or dict."""
        async with api_call(tracker, "GET", "/schedules") as call:
            result = await client.schedules.list()
            call.result = result
            assert isinstance(result, (list, dict))

    async def test_lifecycle(
        self,
        client: Modulex,
        tracker: ResultTracker,
        test_workflow_id: str,
    ) -> None:
        """Full create → get → pause → resume → list_runs → run_stats → delete cycle."""
        if not test_workflow_id:
            skip_call(
                tracker,
                "POST",
                "/schedules",
                reason="MODULEX_TEST_WORKFLOW_ID not set — skipping schedule lifecycle",
            )
            return

        created_id: str | None = None
        try:
            # --- create (may fail if workflow has no deployment) ---
            try:
                async with api_call(tracker, "POST", "/schedules") as call:
                    result = await client.schedules.create(
                        workflow_id=test_workflow_id,
                        name="SDK Integration Test Schedule",
                        schedule_type="interval",
                        interval_seconds=3600,
                    )
                    call.result = result
                    assert isinstance(result, dict)
                    created_id = result.get("id") or result.get("schedule_id")
                    assert created_id, f"No ID in create response: {result}"
            except ModulexError as exc:
                skip_call(tracker, "POST", "/schedules", f"Cannot create schedule: {exc}")
                pytest.skip(f"Cannot create schedule: {exc}")
                return

            # --- get ---
            async with api_call(tracker, "GET", f"/schedules/{created_id}") as call:
                result = await client.schedules.get(created_id)
                call.result = result
                assert isinstance(result, dict)

            # --- pause ---
            async with api_call(tracker, "POST", f"/schedules/{created_id}/pause") as call:
                result = await client.schedules.pause(created_id)
                call.result = result
                assert isinstance(result, (dict, type(None)))

            # --- resume ---
            async with api_call(tracker, "POST", f"/schedules/{created_id}/resume") as call:
                result = await client.schedules.resume(created_id)
                call.result = result
                assert isinstance(result, (dict, type(None)))

            # --- list_runs ---
            async with api_call(tracker, "GET", f"/schedules/{created_id}/runs") as call:
                result = await client.schedules.list_runs(created_id)
                call.result = result
                assert isinstance(result, (list, dict))

            # --- run_stats ---
            async with api_call(tracker, "GET", f"/schedules/{created_id}/runs/stats") as call:
                result = await client.schedules.run_stats(created_id)
                call.result = result
                assert isinstance(result, (list, dict))

        finally:
            if created_id:
                async with api_call(tracker, "DELETE", f"/schedules/{created_id}") as call:
                    await client.schedules.delete(created_id)
