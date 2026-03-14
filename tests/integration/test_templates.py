from __future__ import annotations

import pytest

from modulex import Modulex, NotFoundError
from tests.integration.conftest import ResultTracker, api_call


@pytest.mark.asyncio
class TestTemplates:
    """Integration tests for the /templates endpoints."""

    async def test_list(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /templates — response has a templates key."""
        async with api_call(tracker, "GET", "/templates") as call:
            result = await client.templates.list()
            call.result = result
            assert isinstance(result, dict)
            assert "templates" in result

    async def test_my_templates(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /templates/me — response has a templates key."""
        async with api_call(tracker, "GET", "/templates/me") as call:
            result = await client.templates.my_templates()
            call.result = result
            assert isinstance(result, dict)
            assert "templates" in result

    async def test_my_creator(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /templates/creators/me — may return 404 if no creator profile exists."""
        try:
            async with api_call(tracker, "GET", "/templates/creators/me") as call:
                result = await client.templates.my_creator()
                call.result = result
                assert isinstance(result, dict)
        except NotFoundError:
            # No creator profile for this account — this is an expected outcome
            pass
