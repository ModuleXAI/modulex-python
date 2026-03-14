from __future__ import annotations

import pytest

from modulex import Modulex
from tests.integration.conftest import ResultTracker, api_call, skip_call


@pytest.mark.asyncio
class TestChats:
    """Integration tests for the /chats endpoints."""

    async def test_list(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /chats — chats are returned grouped by folder as a dict."""
        async with api_call(tracker, "GET", "/chats") as call:
            result = await client.chats.list()
            call.result = result
            assert isinstance(result, dict)

    async def test_stream_sse(self, tracker: ResultTracker) -> None:
        """GET /chats/stream — skip; SSE requires an active chat stream."""
        skip_call(
            tracker,
            "GET",
            "/chats/stream",
            reason="SSE requires active chat stream",
        )
