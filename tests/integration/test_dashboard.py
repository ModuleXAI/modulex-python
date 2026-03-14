"""Integration tests for the Dashboard resource.

Covers: logs, analytics_overview, analytics_tools, analytics_llm_usage, users.
"""

from __future__ import annotations

import pytest

from modulex import Modulex
from tests.integration.conftest import ResultTracker, api_call


@pytest.mark.asyncio
class TestDashboard:
    """Live API tests for dashboard endpoints."""

    async def test_logs(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /dashboard/logs — response must contain a 'data' key with a 'logs' subkey."""
        async with api_call(tracker, "GET", "/dashboard/logs") as call:
            result = await client.dashboard.logs()
            call.result = result
            assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"
            assert "data" in result, "'data' key missing from logs response"
            assert "logs" in result["data"], "'logs' subkey missing from response['data']"

    async def test_analytics_overview(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /dashboard/analytics/overview — response must contain a 'data' key."""
        async with api_call(tracker, "GET", "/dashboard/analytics/overview") as call:
            result = await client.dashboard.analytics_overview()
            call.result = result
            assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"
            assert "data" in result, "'data' key missing from analytics overview response"

    async def test_analytics_tools(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /dashboard/analytics/tools — response must be a dict."""
        async with api_call(tracker, "GET", "/dashboard/analytics/tools") as call:
            result = await client.dashboard.analytics_tools()
            call.result = result
            assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"

    async def test_analytics_llm_usage(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /dashboard/analytics/llm-usage — response must be a dict."""
        async with api_call(tracker, "GET", "/dashboard/analytics/llm-usage") as call:
            result = await client.dashboard.analytics_llm_usage()
            call.result = result
            assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"

    async def test_users(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /dashboard/users — response must contain a 'users' key."""
        async with api_call(tracker, "GET", "/dashboard/users") as call:
            result = await client.dashboard.users()
            call.result = result
            assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"
            assert "users" in result, "'users' key missing from dashboard users response"
