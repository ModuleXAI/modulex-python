"""Integration tests for the Notifications resource.

Covers: list, create.
"""

from __future__ import annotations

import pytest

from modulex import Modulex
from tests.integration.conftest import ResultTracker, api_call


@pytest.mark.asyncio
class TestNotifications:
    """Live API tests for notification endpoints."""

    async def test_list(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /notifications — response must contain a 'notifications' key."""
        async with api_call(tracker, "GET", "/notifications") as call:
            result = await client.notifications.list()
            call.result = result
            assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"
            assert "notifications" in result, "'notifications' key missing from list response"

    async def test_create(self, client: Modulex, tracker: ResultTracker) -> None:
        """POST /notifications/organization — broadcast notification must return a success response."""
        async with api_call(tracker, "POST", "/notifications/organization") as call:
            result = await client.notifications.create(
                notification_topic="attention",
                message="SDK integration test notification — safe to ignore",
            )
            call.result = result
            assert result is not None, "create notification response must not be None"
            assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"
