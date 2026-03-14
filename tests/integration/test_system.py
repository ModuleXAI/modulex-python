"""Integration tests for the System resource.

Covers: health, metrics, timezones, search_timezones.
"""

from __future__ import annotations

import pytest

from modulex import Modulex
from tests.integration.conftest import ResultTracker, api_call


@pytest.mark.asyncio
class TestSystem:
    """Live API tests for system-level endpoints."""

    async def test_health(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /system/health — status field must equal 'healthy'."""
        async with api_call(tracker, "GET", "/system/health") as call:
            result = await client.system.health()
            call.result = result
            assert result is not None, "health response must not be None"
            assert result.get("status") == "healthy", f"expected status='healthy', got {result.get('status')!r}"

    async def test_metrics(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /system/metrics — response must be a non-empty string."""
        async with api_call(tracker, "GET", "/system/metrics") as call:
            result = await client.system.metrics()
            call.result = result
            # Prometheus text format returns a string; JSON returns a dict.
            # Both are valid — just assert we got something back.
            assert result is not None and result != "", "metrics response must not be empty"

    async def test_timezones(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /system/timezones — response must contain 'popular' and 'all_timezones' keys."""
        async with api_call(tracker, "GET", "/system/timezones") as call:
            result = await client.system.timezones()
            call.result = result
            assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"
            assert "popular" in result, "'popular' key missing from timezones response"
            assert "all_timezones" in result, "'all_timezones' key missing from timezones response"
            assert isinstance(result["popular"], list), "'popular' must be a list"
            assert isinstance(result["all_timezones"], list), "'all_timezones' must be a list"
            assert len(result["all_timezones"]) > 0, "'all_timezones' must not be empty"

    async def test_search_timezones(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /system/timezones/search?q=Istanbul — results must be non-empty."""
        async with api_call(tracker, "GET", "/system/timezones/search") as call:
            result = await client.system.search_timezones("Istanbul")
            call.result = result
            assert result is not None, "search_timezones response must not be None"
            # Response may be a list or a dict with a results key.
            if isinstance(result, list):
                assert len(result) > 0, "expected at least one timezone matching 'Istanbul'"
                # Each entry should reference Istanbul in some way.
                names = [str(r) for r in result]
                assert any("Istanbul" in n for n in names), "no result contained 'Istanbul' in the timezone name"
            else:
                assert isinstance(result, dict), f"unexpected type {type(result).__name__}"
                # Accept either a 'results' or 'timezones' key.
                items: list[object] = result.get("results") or result.get("timezones") or []
                assert len(items) > 0, "expected at least one timezone matching 'Istanbul'"
