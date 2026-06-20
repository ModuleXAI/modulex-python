"""Tests for the Assistant resource."""

from __future__ import annotations

import json as _json

import httpx
import pytest
import respx

from modulex import Modulex
from modulex.types.realtime import ComposerLLMConfig, YesNoResponse

_SSE_HEADERS = {"content-type": "text/event-stream"}


@pytest.mark.asyncio
class TestAssistant:
    async def test_chat_uses_chat_id_field(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/assistant/chat").mock(
            return_value=httpx.Response(200, json={"status": "running", "chat_id": "a1", "run_id": "r1"})
        )
        await client.assistant.chat(
            "summarize this",
            chat_id="a1",
            llm=ComposerLLMConfig(integration_name="openai", provider_id="openai", model_id="gpt-4o-mini"),
        )
        sent = _json.loads(route.calls.last.request.content)
        assert sent["chat_id"] == "a1"  # assistant uses chat_id (NOT composer_chat_id)
        assert sent["llm"]["model_id"] == "gpt-4o-mini"
        assert sent["message"] == "summarize this"

    async def test_resume_body_shape(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/assistant/chat/a1/resume").mock(
            return_value=httpx.Response(200, json={"status": "resuming", "chat_id": "a1", "run_id": "r2"})
        )
        result = await client.assistant.resume(
            "a1",
            request_id="q-1",
            response=YesNoResponse(answer=False),
            llm={"integration_name": "openai", "provider_id": "openai", "model_id": "gpt-4o-mini"},
        )
        sent = _json.loads(route.calls.last.request.content)
        assert sent["response"] == {"kind": "yes_no", "answer": False}
        assert sent["request_id"] == "q-1"
        assert result["run_id"] == "r2"

    async def test_list_cursor(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.get("/assistant/chats").mock(
            return_value=httpx.Response(200, json={"items": [{"id": "a1"}], "next_cursor": None})
        )
        await client.assistant.list(limit=5, cursor="2024-01-01T00:00:00Z")
        assert route.calls.last.request.url.params["cursor"] == "2024-01-01T00:00:00Z"
        assert route.calls.last.request.url.params["limit"] == "5"

    async def test_listen_normalizes_events(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        body = (
            'data: {"type": "response_chunk", "data": {"text": "hi"}}\n\n'
            'data: {"type": "done", "data": {"response": "done"}}\n\n'
        )
        mock_api.get("/assistant/chat/a1/listen/r1").mock(
            return_value=httpx.Response(200, headers=_SSE_HEADERS, text=body)
        )
        events = [e async for e in client.assistant.listen("a1", "r1")]
        assert [e.event for e in events] == ["response_chunk", "done"]

    async def test_status_and_cancel_and_delete(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/assistant/chat/a1/status").mock(
            return_value=httpx.Response(200, json={"chat_id": "a1", "is_running": False, "awaiting_input": False})
        )
        mock_api.post("/assistant/chat/a1/cancel").mock(
            return_value=httpx.Response(200, json={"status": "cancelled", "chat_id": "a1"})
        )
        delete_route = mock_api.delete("/assistant/chat/a1").mock(
            return_value=httpx.Response(200, json={"status": "deleted", "chat_id": "a1", "permanent": True})
        )
        assert (await client.assistant.status("a1"))["chat_id"] == "a1"
        assert (await client.assistant.cancel("a1"))["status"] == "cancelled"
        result = await client.assistant.delete("a1", permanent=True)
        assert result["permanent"] is True
        assert delete_route.calls.last.request.url.params["permanent"] == "true"
