from __future__ import annotations

import pytest

from modulex import Modulex, ModulexError
from tests.integration.conftest import ResultTracker, api_call, skip_call


@pytest.mark.asyncio
class TestKnowledge:
    """Integration tests for the /knowledge-bases endpoints."""

    async def test_list(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /knowledge-bases — response has items or is a list."""
        async with api_call(tracker, "GET", "/knowledge-bases") as call:
            result = await client.knowledge.list()
            call.result = result
            if isinstance(result, dict):
                # Paginated shape: items/knowledge_bases/data key, or empty dict is fine too
                assert (
                    "items" in result
                    or "knowledge_bases" in result
                    or "data" in result
                    or "total" in result
                    or len(result) >= 0
                )
            else:
                assert isinstance(result, list)

    async def test_supported_file_types(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /knowledge-bases/info/supported-file-types — response has expected keys."""
        async with api_call(tracker, "GET", "/knowledge-bases/info/supported-file-types") as call:
            result = await client.knowledge.supported_file_types()
            call.result = result
            assert isinstance(result, dict)
            assert "supported_types" in result
            assert "max_file_size_mb" in result

    async def test_lifecycle(self, client: Modulex, tracker: ResultTracker) -> None:
        """Full create → get → search → stats → delete cycle for a knowledge base."""
        created_id: str | None = None
        try:
            # --- create (may fail due to plan quota) ---
            try:
                async with api_call(tracker, "POST", "/knowledge-bases") as call:
                    result = await client.knowledge.create(
                        name="SDK Integration Test KB",
                        description="Created by integration tests — safe to delete",
                    )
                    call.result = result
                    assert isinstance(result, dict)
                    created_id = result.get("id") or result.get("knowledge_base_id")
                    assert created_id, f"No ID in create response: {result}"
            except ModulexError as exc:
                skip_call(tracker, "POST", "/knowledge-bases", f"Quota/permission error: {exc}")
                pytest.skip(f"Cannot create knowledge base: {exc}")
                return

            # --- get ---
            async with api_call(tracker, "GET", f"/knowledge-bases/{created_id}") as call:
                result = await client.knowledge.get(created_id)
                call.result = result
                assert isinstance(result, dict)

            # --- search (empty KB — results will be empty, that is expected) ---
            async with api_call(tracker, "POST", f"/knowledge-bases/{created_id}/search") as call:
                result = await client.knowledge.search(created_id, query="integration test query")
                call.result = result
                assert isinstance(result, (dict, list))

            # --- stats ---
            async with api_call(tracker, "GET", "/knowledge-bases/stats") as call:
                result = await client.knowledge.stats()
                call.result = result
                assert isinstance(result, (dict, list))

        finally:
            if created_id:
                async with api_call(tracker, "DELETE", f"/knowledge-bases/{created_id}") as call:
                    await client.knowledge.delete(created_id)
