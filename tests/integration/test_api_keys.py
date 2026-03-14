"""Integration tests for the ApiKeys resource.

Covers full CRUD lifecycle: create, list, get, revoke.
All steps run in a single test function to guarantee ordering, with cleanup
in a finally block so the test key is always revoked even on assertion failure.
"""

from __future__ import annotations

import pytest

from modulex import Modulex
from tests.integration.conftest import ResultTracker, api_call

_KEY_NAME = "SDK Integration Test Key"


@pytest.mark.asyncio
class TestApiKeys:
    """Live API tests for API key management endpoints."""

    async def test_crud_lifecycle(self, client: Modulex, tracker: ResultTracker) -> None:
        """POST /api-keys → GET /api-keys → GET /api-keys/{id} → DELETE /api-keys/{id}.

        Creates a named key, verifies it appears in the list, fetches it by ID,
        then revokes it. Cleanup runs in a finally block so the key is always removed.
        """
        created_id: str | None = None

        try:
            # --- CREATE ---
            async with api_call(tracker, "POST", "/api-keys") as call:
                created = await client.api_keys.create(_KEY_NAME)
                call.result = created
                assert isinstance(created, dict), f"create response must be a dict, got {type(created).__name__}"
                assert "id" in created, "'id' key missing from create response"
                assert created.get("name") == _KEY_NAME, f"expected name={_KEY_NAME!r}, got {created.get('name')!r}"
                created_id = created["id"]

            # --- LIST ---
            async with api_call(tracker, "GET", "/api-keys") as call:
                listing = await client.api_keys.list()
                call.result = listing
                # Response may be a list or a dict wrapping a list.
                if isinstance(listing, list):
                    keys = listing
                else:
                    assert isinstance(listing, dict), (
                        f"list response must be a list or dict, got {type(listing).__name__}"
                    )
                    keys = listing.get("api_keys") or listing.get("keys") or listing.get("data") or []

                ids = [k.get("id") for k in keys if isinstance(k, dict)]
                assert created_id in ids, f"newly created key {created_id!r} not found in list response"

            # --- GET BY ID ---
            async with api_call(tracker, "GET", f"/api-keys/{created_id}") as call:
                fetched = await client.api_keys.get(created_id)
                call.result = fetched
                assert isinstance(fetched, dict), f"get response must be a dict, got {type(fetched).__name__}"
                assert fetched.get("id") == created_id, (
                    f"get returned id={fetched.get('id')!r}, expected {created_id!r}"
                )
                assert fetched.get("name") == _KEY_NAME, (
                    f"get returned name={fetched.get('name')!r}, expected {_KEY_NAME!r}"
                )

        finally:
            if created_id:
                # --- REVOKE ---
                async with api_call(tracker, "DELETE", f"/api-keys/{created_id}") as call:
                    revoke_result = await client.api_keys.revoke(created_id)
                    call.result = revoke_result
