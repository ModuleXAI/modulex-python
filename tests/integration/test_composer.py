"""Integration tests for the Composer resource.

All tests are skipped because the composer endpoints require an active workflow
session that cannot be created safely in an automated integration test run.
"""

from __future__ import annotations

import pytest

from tests.integration.conftest import ResultTracker, skip_call


@pytest.mark.asyncio
class TestComposer:
    """Live API tests for composer endpoints — all skipped due to session requirements."""

    async def test_chat(self, tracker: ResultTracker) -> None:
        """POST /composer/chat — skip; requires an active workflow for the composer."""
        skip_call(
            tracker,
            "POST",
            "/composer/chat",
            reason="Requires active workflow for composer",
        )

    async def test_listen_sse(self, tracker: ResultTracker) -> None:
        """GET /composer/chat/.../listen/... — skip; SSE requires active composer session."""
        skip_call(
            tracker,
            "GET",
            "/composer/chat/.../listen/...",
            reason="SSE requires active composer session",
        )
