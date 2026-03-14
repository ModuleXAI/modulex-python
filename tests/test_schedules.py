"""Tests for the Schedules resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from modulex import Modulex


@pytest.mark.asyncio
class TestSchedules:
    async def test_create(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/schedules").mock(
            return_value=httpx.Response(
                201,
                json={
                    "id": "sched-123",
                    "workflow_id": "wf-123",
                    "name": "Daily",
                    "schedule_type": "cron",
                    "is_active": True,
                },
            )
        )
        result = await client.schedules.create(
            workflow_id="wf-123",
            name="Daily",
            schedule_type="cron",
            cron_expression="0 9 * * *",
        )
        assert result["id"] == "sched-123"

    async def test_list(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/schedules").mock(return_value=httpx.Response(200, json={"items": [], "total": 0}))
        result = await client.schedules.list()
        assert result["total"] == 0

    async def test_pause(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/schedules/sched-123/pause").mock(
            return_value=httpx.Response(200, json={"id": "sched-123", "is_active": False})
        )
        result = await client.schedules.pause("sched-123")
        assert result["is_active"] is False

    async def test_resume(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/schedules/sched-123/resume").mock(
            return_value=httpx.Response(200, json={"id": "sched-123", "is_active": True})
        )
        result = await client.schedules.resume("sched-123")
        assert result["is_active"] is True

    async def test_run_stats(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/schedules/sched-123/runs/stats").mock(
            return_value=httpx.Response(
                200,
                json={
                    "total_runs": 100,
                    "successful_runs": 95,
                    "failed_runs": 5,
                },
            )
        )
        result = await client.schedules.run_stats("sched-123", days=30)
        assert result["total_runs"] == 100

    async def test_retry_run(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/schedules/sched-123/runs/run-456/retry").mock(
            return_value=httpx.Response(200, json={"id": "run-new", "status": "pending"})
        )
        result = await client.schedules.retry_run("sched-123", "run-456")
        assert result["status"] == "pending"
