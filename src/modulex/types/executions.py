"""Execution-related type definitions."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class RunResponse(TypedDict, total=False):
    """Response from /workflows/run."""

    status: str
    run_id: str
    thread_id: str
    chat_id: str | None
    ephemeral: bool
    stream: bool
    workflow_name: str
    workflow_version: str
    workflow_source: str
    elapsed_ms: float
    human_message: dict[str, Any]
    ai_message: dict[str, Any]
    message: str


class StateResponse(TypedDict, total=False):
    """Response from /workflows/state/{thread_id}."""

    thread_id: str
    run_id: str
    checkpoint_id: str
    state: dict[str, Any]
    next: list[str]
    metadata: dict[str, Any]
    pending_writes: int


class ResumeResponse(TypedDict, total=False):
    """Response from /workflows/resume/{thread_id}."""

    status: str
    run_id: str
    thread_id: str
    stream: bool
    workflow_source: str
    message: str


class CancelResponse(TypedDict, total=False):
    """Response from /workflows/cancel/{run_id}."""

    status: str
    run_id: str
    reason: str
    message: str


class NodeUpdateEvent(TypedDict, total=False):
    """SSE node_update event data."""

    node_id: str
    node_type: str
    status: str
    output: dict[str, Any]
    error: str | None
    execution_time_ms: float


class MetadataEvent(TypedDict, total=False):
    """SSE metadata event data."""

    run_id: str
    thread_id: str
    workflow_name: str
    workflow_version: str
    nodes: list[dict[str, Any]]


class InterruptEvent(TypedDict, total=False):
    """SSE interrupt event data."""

    message: str
    state: dict[str, Any]
    resume_instructions: str
    node_id: str


class DoneEvent(TypedDict, total=False):
    """SSE done event data."""

    final_state: dict[str, Any]
    steps_executed: int
    total_execution_time_ms: float


class ErrorEvent(TypedDict, total=False):
    """SSE error event data."""

    error_message: str
    error_type: str
    node_id: str | None
    stack_trace: str | None
