"""Executions resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource
from modulex._streaming import EventSourceStream


class Executions(_BaseResource):
    """Resource for running and managing workflow executions."""

    async def run(
        self,
        *,
        workflow_id: str | None = None,
        workflow: dict[str, Any] | None = None,
        llm: dict[str, Any] | None = None,
        system_workflow: str | None = None,
        input: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
        stream: bool = True,
        ephemeral: bool = False,
        is_private: bool = False,
        knowledge_config: dict[str, Any] | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Trigger a workflow execution and return the run result or stream handle."""
        body: dict[str, Any] = {
            "stream": stream,
            "ephemeral": ephemeral,
            "is_private": is_private,
        }
        if workflow_id is not None:
            body["workflow_id"] = workflow_id
        if workflow is not None:
            body["workflow"] = workflow
        if llm is not None:
            body["llm"] = llm
        if system_workflow is not None:
            body["system_workflow"] = system_workflow
        if input is not None:
            body["input"] = input
        if config is not None:
            body["config"] = config
        if knowledge_config is not None:
            body["knowledge_config"] = knowledge_config
        return await self._post("/workflows/run", json=body, organization_id=organization_id)

    async def get_state(self, thread_id: str, *, organization_id: str | None = None) -> Any:
        """Return the current state of a workflow thread."""
        return await self._get(f"/workflows/state/{thread_id}", organization_id=organization_id)

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
    ) -> Any:
        """Resume a paused workflow thread with the provided resume value."""
        body: dict[str, Any] = {
            "run_id": run_id,
            "resume_value": resume_value,
            "stream": stream,
        }
        if workflow_id is not None:
            body["workflow_id"] = workflow_id
        if workflow is not None:
            body["workflow"] = workflow
        return await self._post(f"/workflows/resume/{thread_id}", json=body, organization_id=organization_id)

    async def cancel(
        self,
        run_id: str,
        *,
        reason: str | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Cancel an in-progress workflow run by its run ID."""
        body: dict[str, Any] = {}
        if reason is not None:
            body["reason"] = reason
        return await self._post(
            f"/workflows/cancel/{run_id}",
            json=body or None,
            organization_id=organization_id,
        )

    def listen(self, run_id: str, *, organization_id: str | None = None) -> EventSourceStream:
        """Open an SSE stream to receive live events for a workflow run."""
        return self._stream_sse(f"/workflows/listen/{run_id}", organization_id=organization_id)
