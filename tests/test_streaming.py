"""Tests for SSE streaming and the dual wire-format normalization."""

from __future__ import annotations

import httpx
import pytest
import respx

from modulex import Modulex
from modulex._exceptions import AuthenticationError, NotFoundError
from modulex._streaming import SSEEvent

_SSE_HEADERS = {"content-type": "text/event-stream"}


class TestSSEEvent:
    def test_create_event(self) -> None:
        event = SSEEvent(event="node_update", data={"node_id": "n1", "status": "completed"})
        assert event.event == "node_update"
        assert event.data["node_id"] == "n1"
        assert event.id is None
        assert event.retry is None
        assert event.raw_event is None
        assert event.is_terminal is False

    def test_event_with_all_fields(self) -> None:
        event = SSEEvent(event="done", data={"steps": 5}, id="evt-1", retry=3000, raw_event="message")
        assert event.id == "evt-1"
        assert event.retry == 3000
        assert event.raw_event == "message"
        assert event.is_terminal is True  # "done" is terminal


@pytest.mark.asyncio
class TestEventSourceNormalization:
    async def test_b_group_reads_type_from_data(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        """workflow/composer/assistant streams: event name lives in data['type']."""
        body = (
            'data: {"type": "metadata", "workflow_type": "workflow"}\n\n'
            'data: {"type": "node_update", "node_id": "n1", "status": "completed"}\n\n'
            'data: {"type": "done", "steps_executed": 3}\n\n'
        )
        mock_api.get("/workflows/listen/run-1").mock(return_value=httpx.Response(200, headers=_SSE_HEADERS, text=body))
        events = [e async for e in client.executions.listen("run-1")]
        assert [e.event for e in events] == ["metadata", "node_update", "done"]
        assert events[1].data["node_id"] == "n1"

    async def test_a_group_reads_sse_event_field(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        """/chats/stream uses real SSE event: lines."""
        body = (
            "event: connected\n"
            'data: {"status": "connected"}\n\n'
            "event: chat_list_updated\n"
            'data: {"type_label": "public"}\n\n'
        )
        mock_api.get("/chats/stream").mock(return_value=httpx.Response(200, headers=_SSE_HEADERS, text=body))
        events = [e async for e in client.chats.stream()]
        assert [e.event for e in events] == ["connected", "chat_list_updated"]
        assert events[0].raw_event == "connected"

    async def test_heartbeat_filtered_by_default(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        body = (
            'data: {"type": "node_update", "node_id": "n1"}\n\n'
            'data: {"type": "heartbeat"}\n\n'
            'data: {"type": "done"}\n\n'
        )
        mock_api.get("/workflows/listen/run-1").mock(return_value=httpx.Response(200, headers=_SSE_HEADERS, text=body))
        events = [e async for e in client.executions.listen("run-1")]
        assert [e.event for e in events] == ["node_update", "done"]

    async def test_stops_after_terminal_event(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        body = (
            'data: {"type": "node_update", "node_id": "n1"}\n\n'
            'data: {"type": "done", "steps_executed": 1}\n\n'
            'data: {"type": "node_update", "node_id": "n2"}\n\n'  # must NOT be yielded
        )
        mock_api.get("/workflows/listen/run-1").mock(return_value=httpx.Response(200, headers=_SSE_HEADERS, text=body))
        events = [e async for e in client.executions.listen("run-1")]
        assert [e.event for e in events] == ["node_update", "done"]

    async def test_connect_error_is_typed(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        """A 4xx on stream connect surfaces a typed exception, not StreamError."""
        mock_api.get("/workflows/listen/run-1").mock(
            return_value=httpx.Response(401, json={"detail": "Invalid API key"})
        )
        with pytest.raises(AuthenticationError):
            async for _ in client.executions.listen("run-1"):
                pass

    async def test_listen_ownership_404_raises_not_found(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        """A run not owned by your org returns 404 on connect → NotFoundError (no hang, no reconnect)."""
        route = mock_api.get("/workflows/listen/run-x").mock(
            return_value=httpx.Response(404, json={"detail": "Not found"})
        )
        with pytest.raises(NotFoundError):
            async for _ in client.executions.listen("run-x"):
                pass
        assert route.call_count == 1  # NotFoundError, not a StreamError-driven reconnect loop

    async def test_composer_listen_ownership_404_raises_not_found(
        self, client: Modulex, mock_api: respx.MockRouter
    ) -> None:
        """Same ownership 404 contract holds for the composer/assistant listen family."""
        route = mock_api.get("/composer/chat/chat-x/listen/run-x").mock(
            return_value=httpx.Response(404, json={"detail": "Not found"})
        )
        with pytest.raises(NotFoundError):
            async for _ in client.composer.listen("chat-x", "run-x"):
                pass
        assert route.call_count == 1
