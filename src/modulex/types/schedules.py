"""Schedule-related response models (Pydantic v2)."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class ScheduleResponse(ModulexModel):
    """A workflow schedule (POST/GET/PUT /schedules[/{id}])."""

    id: str
    workflow_id: Optional[str] = None
    organization_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    schedule_type: Optional[str] = None
    interval_seconds: Optional[int] = None
    cron_expression: Optional[str] = None
    timezone: Optional[str] = None
    input: dict[str, Any] = Field(default_factory=dict)
    config: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = False
    next_run_at: Optional[str] = None
    last_run_at: Optional[str] = None
    last_run_status: Optional[str] = None
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ScheduleRunResponse(ModulexModel):
    """A single execution triggered by a schedule (GET /schedules/{id}/runs/{run_id})."""

    id: str
    schedule_id: Optional[str] = None
    workflow_id: Optional[str] = None
    run_id: Optional[str] = None
    thread_id: Optional[str] = None
    scheduled_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    triggered_by: Optional[str] = None
    deployment_id: Optional[str] = None
    created_at: Optional[str] = None


class ScheduleStatsResponse(ModulexModel):
    """Aggregate run statistics for a schedule (GET /schedules/{id}/runs/stats)."""

    period_days: int = 0
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    success_rate: float = 0.0
    avg_duration_seconds: Optional[float] = None
    min_duration_seconds: Optional[float] = None
    max_duration_seconds: Optional[float] = None


class ScheduleListResponse(ModulexModel):
    """Response from GET /schedules."""

    schedules: list[ScheduleResponse] = Field(default_factory=list)
    total: int = 0
    limit: int = 0
    offset: int = 0


class ScheduleRunsResponse(ModulexModel):
    """Response from GET /schedules/{id}/runs."""

    runs: list[ScheduleRunResponse] = Field(default_factory=list)
    total: int = 0
    limit: int = 0
    offset: int = 0


class DeleteScheduleResponse(ModulexModel):
    """Response from DELETE /schedules/{id}."""

    message: Optional[str] = None


class RetryRunResponse(ModulexModel):
    """Response from POST /schedules/{id}/runs/{run_id}/retry."""

    message: Optional[str] = None
    original_run_id: Optional[str] = None


# Backward-compatible alias: the pre-migration types file exported ``RunStatsResponse``.
RunStatsResponse = ScheduleStatsResponse
