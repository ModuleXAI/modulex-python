"""Execution / workflow-run response models (Pydantic v2)."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class RunResponse(ModulexModel):
    """Response from POST /workflows/run."""

    status: Optional[str] = None
    run_id: Optional[str] = None
    thread_id: Optional[str] = None
    chat_id: Optional[str] = None
    ephemeral: bool = False
    stream: bool = False
    workflow_name: Optional[str] = None
    workflow_version: Optional[str] = None
    workflow_source: Optional[str] = None
    elapsed_ms: Optional[float] = None
    human_message: Optional[dict[str, Any]] = None
    ai_message: Optional[dict[str, Any]] = None
    message: Optional[str] = None


class StateResponse(ModulexModel):
    """Response from GET /workflows/state/{thread_id}."""

    thread_id: Optional[str] = None
    run_id: Optional[str] = None
    checkpoint_id: Optional[str] = None
    state: Optional[dict[str, Any]] = None
    next: list[Any] = Field(default_factory=list)
    metadata: Optional[dict[str, Any]] = None
    pending_writes: int = 0


class ResumeResponse(ModulexModel):
    """Response from POST /workflows/resume/{thread_id}."""

    status: Optional[str] = None
    run_id: Optional[str] = None
    thread_id: Optional[str] = None
    stream: bool = False
    workflow_source: Optional[str] = None
    message: Optional[str] = None


class CancelResponse(ModulexModel):
    """Response from POST /workflows/cancel/{run_id}."""

    status: Optional[str] = None
    run_id: Optional[str] = None
    reason: Optional[str] = None
    message: Optional[str] = None


class WorkflowRunListItem(ModulexModel):
    """A preview-optimized workflow run row (GET /workflow-runs item)."""

    id: str
    run_id: Optional[str] = None
    workflow_id: Optional[str] = None
    trigger_type: Optional[str] = None
    is_ad_hoc: bool = False
    status: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    has_output: bool = False


class WorkflowRunListResponse(ModulexModel):
    """Response from GET /workflow-runs."""

    runs: list[WorkflowRunListItem] = Field(default_factory=list)
    has_more: bool = False
    limit: int = 0
    offset: int = 0


class WorkflowRunDetail(ModulexModel):
    """A single workflow run's full record (GET /workflow-runs/{run_pk})."""

    id: str
    run_id: Optional[str] = None
    organization_id: Optional[str] = None
    workflow_id: Optional[str] = None
    trigger_type: Optional[str] = None
    is_ad_hoc: bool = False
    status: Optional[str] = None
    user_id: Optional[str] = None
    api_key_id: Optional[str] = None
    schedule_id: Optional[str] = None
    composer_chat_id: Optional[str] = None
    thread_id: Optional[str] = None
    chat_id: Optional[str] = None
    deployment_id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    input_snapshot: Optional[Any] = None
    output_summary: Optional[Any] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ---------------------------------------------------------------------------
# SSE workflow run events (NOT returned by any method; listen() yields raw
# SSEEvent objects). The backend's "design" Pydantic models and its runtime
# emission disagree on payload shape, so these are intentionally tolerant
# (all fields Optional, extra="allow") and are never bound to a return type.
# ---------------------------------------------------------------------------


class WorkflowRunEvent(ModulexModel):
    """Tolerant base for any workflow run SSE event payload (``data['type']``)."""

    type: Optional[str] = None
    run_id: Optional[str] = None
    thread_id: Optional[str] = None
    timestamp: Optional[str] = None
    node: Optional[str] = None
    name: Optional[str] = None
    output: Optional[Any] = None
    data: Optional[Any] = None
    message: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
