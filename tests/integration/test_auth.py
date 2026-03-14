"""Integration tests for the Auth resource.

Covers: me, organizations.
"""

from __future__ import annotations

import pytest

from modulex import Modulex
from tests.integration.conftest import ResultTracker, api_call


@pytest.mark.asyncio
class TestAuth:
    """Live API tests for authentication and identity endpoints."""

    async def test_me(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /auth/me — response must contain 'id' and 'email'."""
        async with api_call(tracker, "GET", "/auth/me") as call:
            result = await client.auth.me()
            call.result = result
            assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"
            assert "id" in result, "'id' key missing from /auth/me response"
            assert "email" in result, "'email' key missing from /auth/me response"
            assert result["id"], "'id' must be a non-empty value"
            assert result["email"], "'email' must be a non-empty value"

    async def test_organizations(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /auth/me/organizations — response must contain 'organizations' key."""
        async with api_call(tracker, "GET", "/auth/me/organizations") as call:
            result = await client.auth.organizations()
            call.result = result
            assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"
            assert "organizations" in result, "'organizations' key missing from /auth/me/organizations response"
            assert isinstance(result["organizations"], list), "'organizations' must be a list"
