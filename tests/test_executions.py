"""Tests for the Executions resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from modulex import Modulex


@pytest.mark.asyncio
class TestExecutions:
    async def test_run_with_workflow_id(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/workflows/run").mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "running",
                    "run_id": "run-123",
                    "thread_id": "thread-123",
                    "stream": True,
                    "workflow_source": "database",
                },
            )
        )
        result = await client.executions.run(
            workflow_id="wf-123",
            input={"messages": [{"role": "user", "content": "Hello"}]},
        )
        assert result["status"] == "running"
        assert result["run_id"] == "run-123"

    async def test_run_with_adhoc_workflow(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/workflows/run").mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "running",
                    "run_id": "run-456",
                    "workflow_source": "request",
                },
            )
        )
        result = await client.executions.run(
            workflow={"nodes": [], "edges": [], "entry_point": "start"},
            input={},
        )
        assert result["workflow_source"] == "request"

    async def test_run_with_llm(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/workflows/run").mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "running",
                    "run_id": "run-789",
                    "workflow_source": "llm",
                },
            )
        )
        result = await client.executions.run(
            llm={
                "integration_name": "openai",
                "provider_id": "openai",
                "model_id": "gpt-4o-mini",
            },
            input={"messages": [{"role": "user", "content": "Hi"}]},
        )
        assert result["workflow_source"] == "llm"

    async def test_run_with_system_workflow(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/workflows/run").mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "running",
                    "run_id": "run-sys",
                    "workflow_source": "system:my_workflow",
                },
            )
        )
        result = await client.executions.run(
            system_workflow="my_workflow",
            input={},
        )
        assert "system:" in result["workflow_source"]

    async def test_get_state(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/workflows/state/thread-123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "thread_id": "thread-123",
                    "run_id": "run-123",
                    "state": {"messages": []},
                    "next": ["node_2"],
                    "pending_writes": 0,
                },
            )
        )
        result = await client.executions.get_state("thread-123")
        assert result["thread_id"] == "thread-123"
        assert result["next"] == ["node_2"]

    async def test_resume(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/workflows/resume/thread-123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "resumed",
                    "run_id": "run-new",
                    "thread_id": "thread-123",
                    "stream": True,
                },
            )
        )
        result = await client.executions.resume(
            thread_id="thread-123",
            run_id="run-123",
            resume_value="user input here",
        )
        assert result["status"] == "resumed"

    async def test_cancel(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/workflows/cancel/run-123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "cancellation_requested",
                    "run_id": "run-123",
                    "reason": "No longer needed",
                },
            )
        )
        result = await client.executions.cancel("run-123", reason="No longer needed")
        assert result["status"] == "cancellation_requested"
