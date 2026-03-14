"""SSE streaming support for the ModuleX SDK."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import httpx
from httpx_sse import aconnect_sse

from modulex._exceptions import StreamError


@dataclass
class SSEEvent:
    """A Server-Sent Event."""

    event: str
    data: dict[str, Any]
    id: str | None = None
    retry: int | None = None


class SSEStream:
    """Async iterator for Server-Sent Events streams."""

    def __init__(self, response: httpx.Response) -> None:
        self._response = response
        self._closed = False

    def __aiter__(self) -> AsyncIterator[SSEEvent]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[SSEEvent]:
        """Iterate over SSE events from the response."""
        try:
            async for line in self._response.aiter_lines():
                if self._closed:
                    break

                line = line.strip()
                if not line or line.startswith(":"):
                    continue

                event = self._parse_event(line)
                if event and event.event != "keepalive":
                    yield event
        except httpx.StreamClosed:
            return
        except Exception as e:
            if not self._closed:
                raise StreamError(f"SSE stream error: {e}") from e

    @staticmethod
    def _parse_event(line: str) -> SSEEvent | None:
        """Parse a single SSE line into an event."""
        if line.startswith("data:"):
            data_str = line[5:].strip()
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                data = {"raw": data_str}
            return SSEEvent(event="message", data=data)
        return None

    async def close(self) -> None:
        """Close the SSE stream."""
        self._closed = True
        await self._response.aclose()


class EventSourceStream:
    """Full SSE parser that handles multi-line event blocks."""

    def __init__(self, client: httpx.AsyncClient, method: str, url: str, **kwargs: Any) -> None:
        self._client = client
        self._method = method
        self._url = url
        self._kwargs = kwargs
        self._closed = False

    def __aiter__(self) -> AsyncIterator[SSEEvent]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[SSEEvent]:
        """Connect and iterate over SSE events."""
        try:
            async with aconnect_sse(self._client, self._method, self._url, **self._kwargs) as event_source:
                async for sse in event_source.aiter_sse():
                    if self._closed:
                        break

                    event_type = sse.event or "message"
                    if event_type == "keepalive":
                        continue

                    try:
                        data = json.loads(sse.data) if sse.data else {}
                    except json.JSONDecodeError:
                        data = {"raw": sse.data}

                    yield SSEEvent(
                        event=event_type,
                        data=data,
                        id=sse.id,
                        retry=sse.retry,
                    )
        except httpx.StreamClosed:
            return
        except Exception as e:
            if not self._closed:
                raise StreamError(f"SSE stream error: {e}") from e

    async def close(self) -> None:
        """Close the SSE stream."""
        self._closed = True
