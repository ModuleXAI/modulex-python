"""Executions resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource
from modulex._streaming import EventSourceStream
from modulex.types._models import AsyncPage
from modulex.types.executions import (
    CancelResponse,
    ResumeResponse,
    RunResponse,
    StateResponse,
    WorkflowRunDetail,
    WorkflowRunListItem,
    WorkflowRunListResponse,
)


class Executions(_BaseResource):
    """Resource for running and managing workflow executions."""

    async def run(
        self,
        *,
        workflow_id: str | None = None,
        workflow: dict[str, Any] | None = None,
        system_workflow: str | None = None,
        input: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
        stream: bool = True,
        ephemeral: bool = False,
        is_private: bool = False,
        attribution_workflow_id: str | None = None,
        idempotency_key: str | None = None,
        organization_id: str | None = None,
    ) -> RunResponse:
        """Trigger a workflow execution and return the run result or stream handle.

        Use ``workflow_id`` (deployed workflow), ``workflow`` (ad-hoc definition),
        or ``system_workflow``. ``attribution_workflow_id`` links an ad-hoc run to a
        workflow's Runs panel. Pass a stable ``idempotency_key`` to safely retry a
        run without double-execution. The LLM ("agentic") mode was removed from this
        endpoint — use ``client.assistant.chat()`` instead.
        """
        body: dict[str, Any] = {
            "stream": stream,
            "ephemeral": ephemeral,
            "is_private": is_private,
        }
        if workflow_id is not None:
            body["workflow_id"] = workflow_id
        if workflow is not None:
            body["workflow"] = workflow
        if system_workflow is not None:
            body["system_workflow"] = system_workflow
        if input is not None:
            body["input"] = input
        if config is not None:
            body["config"] = config
        if attribution_workflow_id is not None:
            body["attribution_workflow_id"] = attribution_workflow_id
        return RunResponse.model_validate(
            await self._post(
                "/workflows/run",
                json=body,
                organization_id=organization_id,
                idempotency_key=idempotency_key,
            )
        )

    async def get_state(self, thread_id: str, *, organization_id: str | None = None) -> StateResponse:
        """Return the current state of a workflow thread.

        A 404 (``NotFoundError``) means the thread was not found or is not owned by
        your org (identical 404 in both cases — no existence leak).
        """
        return StateResponse.model_validate(
            await self._get(f"/workflows/state/{thread_id}", organization_id=organization_id)
        )

    async def resume(
        self,
        thread_id: str,
        run_id: str,
        resume_value: Any,
        *,
        workflow_id: str | None = None,
        workflow: dict[str, Any] | None = None,
        stream: bool = True,
        organization_id: str | None = None,
    ) -> ResumeResponse:
        """Resume a paused workflow thread with the provided resume value.

        A 404 (``NotFoundError``) means the thread was not found or is not owned by
        your org (identical 404 in both cases — no existence leak).
        """
        body: dict[str, Any] = {
            "run_id": run_id,
            "resume_value": resume_value,
            "stream": stream,
        }
        if workflow_id is not None:
            body["workflow_id"] = workflow_id
        if workflow is not None:
            body["workflow"] = workflow
        return ResumeResponse.model_validate(
            await self._post(f"/workflows/resume/{thread_id}", json=body, organization_id=organization_id)
        )

    async def cancel(
        self,
        run_id: str,
        *,
        reason: str | None = None,
        organization_id: str | None = None,
    ) -> CancelResponse:
        """Cancel an in-progress workflow run by its run ID.

        A 404 (``NotFoundError``) means the run was not found or is not owned by
        your org (identical 404 in both cases — no existence leak).
        """
        body: dict[str, Any] = {}
        if reason is not None:
            body["reason"] = reason
        return CancelResponse.model_validate(
            await self._post(
                f"/workflows/cancel/{run_id}",
                json=body or None,
                organization_id=organization_id,
            )
        )

    def listen(self, run_id: str, *, organization_id: str | None = None) -> EventSourceStream:
        """Open an SSE stream to receive live events for a workflow run.

        Event types are carried in ``event.event`` (normalized from ``data['type']``).
        See :data:`modulex.types.realtime.WORKFLOW_EVENT_TYPES`.

        A 404 (``NotFoundError``) on connect means the run was not found or is not
        owned by your org — iterating the stream raises it rather than yielding
        events (no reconnect loop, no existence leak).
        """
        return self._stream_sse(f"/workflows/listen/{run_id}", organization_id=organization_id)

    async def list_runs(
        self,
        *,
        workflow_id: str | None = None,
        status: str | None = None,
        trigger_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> WorkflowRunListResponse:
        """List durable workflow runs for the organization (newest first).

        Filter by ``workflow_id`` / ``status`` / ``trigger_type``. Returns one page
        ({runs, has_more, limit, offset}); use :meth:`iter_runs` to auto-paginate.
        """
        params: dict[str, Any] = {
            "workflow_id": workflow_id,
            "status": status,
            "trigger_type": trigger_type,
            "limit": limit,
            "offset": offset,
        }
        return WorkflowRunListResponse.model_validate(
            await self._get("/workflow-runs", params=params, organization_id=organization_id)
        )

    def iter_runs(
        self,
        *,
        workflow_id: str | None = None,
        status: str | None = None,
        trigger_type: str | None = None,
        page_size: int = 50,
        organization_id: str | None = None,
    ) -> AsyncPage[WorkflowRunListItem]:
        """Async-iterate over all workflow runs (auto-paginates via ``has_more``)."""
        params: dict[str, Any] = {
            "workflow_id": workflow_id,
            "status": status,
            "trigger_type": trigger_type,
        }
        return AsyncPage(
            self._paginate(
                "/workflow-runs",
                items_key="runs",
                params=params,
                page_size=page_size,
                organization_id=organization_id,
            ),
            WorkflowRunListItem,
        )

    async def get_run(self, run_pk: str, *, organization_id: str | None = None) -> WorkflowRunDetail:
        """Return a single workflow run's full record (input/output snapshots).

        ``run_pk`` is the run's primary key (the ``id`` field from :meth:`list_runs`),
        NOT the executor-minted ``run_id``.
        """
        return WorkflowRunDetail.model_validate(
            await self._get(f"/workflow-runs/{run_pk}", organization_id=organization_id)
        )
