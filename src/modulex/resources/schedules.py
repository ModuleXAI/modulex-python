"""Schedules resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource


class Schedules(_BaseResource):
    """Resource for managing workflow schedules and their execution runs."""

    async def create(
        self,
        workflow_id: str,
        name: str,
        schedule_type: str,
        *,
        interval_seconds: int | None = None,
        cron_expression: str | None = None,
        timezone: str = "UTC",
        description: str | None = None,
        input: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Create a new schedule that triggers a workflow on a defined cadence."""
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "workflow_id": workflow_id,
                "name": name,
                "schedule_type": schedule_type,
                "interval_seconds": interval_seconds,
                "cron_expression": cron_expression,
                "timezone": timezone,
                "description": description,
                "input": input,
                "config": config,
            }.items()
            if v is not None
        }
        return await self._post("/schedules", json=body, organization_id=organization_id)

    async def list(
        self,
        *,
        workflow_id: str | None = None,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> Any:
        """Return all schedules, optionally filtered by workflow or active status."""
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "workflow_id": workflow_id,
                "is_active": is_active,
                "limit": limit,
                "offset": offset,
            }.items()
            if v is not None
        }
        return await self._get("/schedules", params=params, organization_id=organization_id)

    async def get(
        self,
        schedule_id: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Return a single schedule by its ID."""
        return await self._get(f"/schedules/{schedule_id}", organization_id=organization_id)

    async def update(
        self,
        schedule_id: str,
        *,
        organization_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Update an existing schedule with the provided field values."""
        body: dict[str, Any] = {k: v for k, v in kwargs.items() if v is not None}
        return await self._put(f"/schedules/{schedule_id}", json=body, organization_id=organization_id)

    async def delete(
        self,
        schedule_id: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Delete a schedule permanently by its ID."""
        return await self._delete(f"/schedules/{schedule_id}", organization_id=organization_id)

    async def pause(
        self,
        schedule_id: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Pause an active schedule so it no longer triggers new runs."""
        return await self._post(f"/schedules/{schedule_id}/pause", organization_id=organization_id)

    async def resume(
        self,
        schedule_id: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Resume a paused schedule so it resumes triggering runs."""
        return await self._post(f"/schedules/{schedule_id}/resume", organization_id=organization_id)

    async def list_runs(
        self,
        schedule_id: str,
        *,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> Any:
        """Return execution runs for a schedule, optionally filtered by status."""
        params: dict[str, Any] = {
            k: v for k, v in {"status": status, "limit": limit, "offset": offset}.items() if v is not None
        }
        return await self._get(
            f"/schedules/{schedule_id}/runs",
            params=params,
            organization_id=organization_id,
        )

    async def run_stats(
        self,
        schedule_id: str,
        *,
        days: int = 7,
        organization_id: str | None = None,
    ) -> Any:
        """Return aggregated run statistics for a schedule over the given number of days."""
        params: dict[str, Any] = {"days": days}
        return await self._get(
            f"/schedules/{schedule_id}/runs/stats",
            params=params,
            organization_id=organization_id,
        )

    async def get_run(
        self,
        schedule_id: str,
        run_id: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Return a single run record for a schedule by run ID."""
        return await self._get(
            f"/schedules/{schedule_id}/runs/{run_id}",
            organization_id=organization_id,
        )

    async def retry_run(
        self,
        schedule_id: str,
        run_id: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Retry a failed schedule run by its ID."""
        return await self._post(
            f"/schedules/{schedule_id}/runs/{run_id}/retry",
            organization_id=organization_id,
        )
