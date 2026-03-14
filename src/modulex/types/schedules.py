"""Schedule-related type definitions."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class ScheduleResponse(TypedDict, total=False):
    """Response representing a workflow schedule."""

    id: str
    workflow_id: str
    name: str
    description: str | None
    schedule_type: str
    interval_seconds: int | None
    cron_expression: str | None
    timezone: str
    is_active: bool
    input: dict[str, Any]
    config: dict[str, Any]
    next_run_at: str | None
    last_run_at: str | None
    created_at: str
    updated_at: str


class ScheduleRunResponse(TypedDict, total=False):
    """Response representing a single execution triggered by a schedule."""

    id: str
    schedule_id: str
    status: str
    started_at: str
    completed_at: str | None
    duration_ms: float | None
    error: str | None


class RunStatsResponse(TypedDict, total=False):
    """Aggregate run statistics for a schedule."""

    total_runs: int
    successful_runs: int
    failed_runs: int
    average_duration_ms: float | None
