"""Tests for SSE streaming."""

from __future__ import annotations

from modulex._streaming import SSEEvent, SSEStream


class TestSSEEvent:
    def test_create_event(self) -> None:
        event = SSEEvent(event="node_update", data={"node_id": "n1", "status": "completed"})
        assert event.event == "node_update"
        assert event.data["node_id"] == "n1"
        assert event.id is None
        assert event.retry is None

    def test_event_with_all_fields(self) -> None:
        event = SSEEvent(event="done", data={"steps": 5}, id="evt-1", retry=3000)
        assert event.id == "evt-1"
        assert event.retry == 3000


class TestSSEStreamParsing:
    def test_parse_data_line(self) -> None:
        line = 'data: {"node_id": "n1", "status": "completed"}'
        event = SSEStream._parse_event(line)
        assert event is not None
        assert event.event == "message"
        assert event.data["node_id"] == "n1"

    def test_parse_non_json_data(self) -> None:
        line = "data: plain text"
        event = SSEStream._parse_event(line)
        assert event is not None
        assert event.data == {"raw": "plain text"}

    def test_parse_non_data_line(self) -> None:
        event = SSEStream._parse_event("event: node_update")
        assert event is None
