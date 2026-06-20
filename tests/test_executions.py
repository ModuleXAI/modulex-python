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

    async def test_run_with_attribution_workflow_id(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/workflows/run").mock(
            return_value=httpx.Response(200, json={"status": "running", "run_id": "run-789"})
        )
        await client.executions.run(
            workflow={"nodes": [], "edges": []},
            attribution_workflow_id="wf-attr",
            input={},
        )
        import json as _json

        sent = _json.loads(route.calls.last.request.content)
        assert sent["attribution_workflow_id"] == "wf-attr"
        # llm / knowledge_config are no longer part of the run body
        assert "llm" not in sent
        assert "knowledge_config" not in sent

    async def test_run_no_longer_accepts_llm(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        with pytest.raises(TypeError):
            await client.executions.run(llm={"x": 1})  # type: ignore[call-arg]

    async def test_run_sends_idempotency_key_header(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/workflows/run").mock(
            return_value=httpx.Response(200, json={"status": "running", "run_id": "run-1"})
        )
        await client.executions.run(workflow_id="wf-1", idempotency_key="idem-abc")
        assert route.calls.last.request.headers["Idempotency-Key"] == "idem-abc"

    async def test_list_runs(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.get("/workflow-runs").mock(
            return_value=httpx.Response(
                200,
                json={
                    "runs": [{"id": "r1", "run_id": "run-1", "status": "succeeded"}],
                    "has_more": False,
                    "limit": 50,
                    "offset": 0,
                },
            )
        )
        result = await client.executions.list_runs(workflow_id="wf-1", status="succeeded")
        assert result["runs"][0]["id"] == "r1"
        assert route.calls.last.request.url.params["workflow_id"] == "wf-1"
        assert route.calls.last.request.url.params["status"] == "succeeded"

    async def test_iter_runs_autopaginate(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/workflow-runs").mock(
            side_effect=[
                httpx.Response(
                    200, json={"runs": [{"id": "r1"}, {"id": "r2"}], "has_more": True, "limit": 2, "offset": 0}
                ),
                httpx.Response(200, json={"runs": [{"id": "r3"}], "has_more": False, "limit": 2, "offset": 2}),
            ]
        )
        ids = [r["id"] async for r in client.executions.iter_runs(page_size=2)]
        assert ids == ["r1", "r2", "r3"]

    async def test_get_run(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/workflow-runs/r-pk").mock(
            return_value=httpx.Response(200, json={"id": "r-pk", "run_id": "run-1", "status": "succeeded"})
        )
        result = await client.executions.get_run("r-pk")
        assert result["id"] == "r-pk"

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
