"""SSE streaming support for the ModuleX SDK.

The ModuleX backend uses **two** SSE wire conventions:

  A) ``/chats/stream`` emits a real ``event:`` line (event name in the SSE field).
  B) workflow / composer / assistant / credential streams emit raw ``data: {...}``
     with NO ``event:`` line — the real event type lives in ``data["type"]``.

``EventSourceStream`` normalizes both: ``SSEEvent.event`` always carries the
logical event name, whether it came from the SSE ``event:`` field or from
``data["type"]``. This is what makes ``executions.listen()`` / ``composer.listen()``
dispatch correctly instead of seeing every event as ``"message"``.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import httpx
from httpx_sse import aconnect_sse

from modulex._exceptions import ModulexError, StreamError, raise_for_status

#: Event types that terminate a run stream — iteration stops after one is seen.
TERMINAL_EVENT_TYPES = frozenset({"done", "error", "cancelled", "interrupted"})

#: Event types treated as keepalive noise and filtered out by default.
HEARTBEAT_EVENT_TYPES = frozenset({"heartbeat", "keepalive"})


@dataclass
class SSEEvent:
    """A Server-Sent Event with a normalized logical event name.

    ``event`` is the logical name (from the SSE ``event:`` field for A-group
    streams, or from ``data["type"]`` for B-group streams). ``raw_event`` keeps
    the original SSE ``event:`` field for debugging.
    """

    event: str
    data: dict[str, Any]
    id: str | None = None
    retry: int | None = None
    raw_event: str | None = None

    @property
    def is_terminal(self) -> bool:
        """Whether this event terminates the stream (done/error/cancelled/interrupted)."""
        return self.event in TERMINAL_EVENT_TYPES


class EventSourceStream:
    """Async iterator over a Server-Sent Events stream.

    Normalizes the two backend wire conventions, surfaces HTTP errors on connect
    as typed exceptions, filters heartbeats, and stops after a terminal event.
    Usable as an async iterator or async context manager::

        async with client.executions.listen(run_id) as stream:
            async for event in stream:
                ...
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        *,
        include_heartbeats: bool = False,
        **kwargs: Any,
    ) -> None:
        self._client = client
        self._method = method
        self._url = url
        self._include_heartbeats = include_heartbeats
        self._kwargs = kwargs
        self._closed = False
        self.last_event_id: str | None = None

    def __aiter__(self) -> AsyncIterator[SSEEvent]:
        return self._iterate()

    async def __aenter__(self) -> EventSourceStream:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def _iterate(self) -> AsyncIterator[SSEEvent]:
        """Connect and iterate over SSE events."""
        try:
            async with aconnect_sse(self._client, self._method, self._url, **self._kwargs) as event_source:
                response = event_source.response
                if response.status_code >= 400:
                    # Surface auth/billing/rate denials as typed exceptions instead
                    # of an opaque "content type is not text/event-stream" SSEError.
                    await response.aread()
                    raise_for_status(response)

                async for sse in event_source.aiter_sse():
                    if self._closed:
                        break

                    raw_event = sse.event or None
                    try:
                        data = json.loads(sse.data) if sse.data else {}
                    except json.JSONDecodeError:
                        data = {"raw": sse.data}

                    # Normalize: prefer data["type"] (B-group), fall back to the
                    # SSE event: field (A-group). "message" is httpx_sse's default
                    # when no event: line is present, so treat it as "unknown".
                    type_in_data = data.get("type") if isinstance(data, dict) else None
                    event_name = type_in_data or (raw_event if raw_event and raw_event != "message" else "message")

                    if event_name in HEARTBEAT_EVENT_TYPES and not self._include_heartbeats:
                        continue

                    if sse.id:
                        self.last_event_id = sse.id

                    yield SSEEvent(
                        event=event_name,
                        data=data if isinstance(data, dict) else {"raw": data},
                        id=sse.id,
                        retry=sse.retry,
                        raw_event=raw_event,
                    )

                    if event_name in TERMINAL_EVENT_TYPES:
                        break
        except ModulexError:
            # Typed SDK errors (auth/billing/rate from raise_for_status, StreamError)
            # propagate as-is instead of being re-wrapped below.
            raise
        except httpx.StreamClosed:
            return
        except Exception as e:
            if not self._closed:
                raise StreamError(f"SSE stream error: {e}") from e

    async def close(self) -> None:
        """Stop iterating; the underlying connection closes on context exit."""
        self._closed = True
