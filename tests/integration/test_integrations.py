from __future__ import annotations

import pytest

from modulex import Modulex
from tests.integration.conftest import ResultTracker, api_call


@pytest.mark.asyncio
class TestIntegrations:
    """Integration tests for the /integrations endpoints."""

    async def test_browse(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /integrations/browse — response contains items."""
        async with api_call(tracker, "GET", "/integrations/browse") as call:
            result = await client.integrations.browse()
            call.result = result
            # Paginated response is a dict with items; unpaginated is a list
            if isinstance(result, dict):
                assert "items" in result or "integrations" in result or "data" in result or len(result) > 0
            else:
                assert isinstance(result, list)

    async def test_tools(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /integrations/tools — response is a list or dict."""
        async with api_call(tracker, "GET", "/integrations/tools") as call:
            result = await client.integrations.tools()
            call.result = result
            assert isinstance(result, (list, dict))

    async def test_llm_providers(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /integrations/llm-providers — response is a list or dict."""
        async with api_call(tracker, "GET", "/integrations/llm-providers") as call:
            result = await client.integrations.llm_providers()
            call.result = result
            assert isinstance(result, (list, dict))

    async def test_knowledge_providers(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /integrations/knowledge-providers — response is a list or dict."""
        async with api_call(tracker, "GET", "/integrations/knowledge-providers") as call:
            result = await client.integrations.knowledge_providers()
            call.result = result
            assert isinstance(result, (list, dict))
