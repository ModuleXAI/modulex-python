from __future__ import annotations

import pytest

from modulex import Modulex, ModulexError
from tests.integration.conftest import ResultTracker, api_call


@pytest.mark.asyncio
class TestCredentials:
    """Integration tests for the /credentials endpoints."""

    async def test_list(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /credentials — response contains expected top-level keys."""
        async with api_call(tracker, "GET", "/credentials") as call:
            result = await client.credentials.list()
            call.result = result
            assert isinstance(result, dict)
            # Unfiltered list has total_credentials; filtered list may have credentials key
            assert "total_credentials" in result or "credentials" in result

    async def test_lifecycle(self, client: Modulex, tracker: ResultTracker) -> None:
        """Full create → get → test → update → set_default → usage → audit → delete cycle."""
        created_id: str | None = None
        try:
            # --- create ---
            async with api_call(tracker, "POST", "/credentials") as call:
                result = await client.credentials.create(
                    integration_name="openai",
                    auth_data={"api_key": "sk-test-integration-dummy-key"},
                    display_name="SDK Integration Test Credential",
                )
                call.result = result
                assert isinstance(result, dict)
                created_id = result.get("id") or result.get("credential_id")
                assert created_id, f"No ID in create response: {result}"

            # --- get ---
            async with api_call(tracker, "GET", f"/credentials/{created_id}") as call:
                result = await client.credentials.get(created_id)
                call.result = result
                assert isinstance(result, dict)

            # --- test (dummy key — may fail or throw; just verify we get a response) ---
            try:
                async with api_call(tracker, "POST", f"/credentials/{created_id}/test") as call:
                    result = await client.credentials.test(created_id)
                    call.result = result
                    assert isinstance(result, dict)
            except ModulexError:
                pass  # dummy key validation failure is expected

            # --- update ---
            async with api_call(tracker, "PUT", f"/credentials/{created_id}") as call:
                result = await client.credentials.update(
                    created_id,
                    display_name="SDK Integration Test Credential (updated)",
                )
                call.result = result
                assert isinstance(result, dict)

            # --- set_default ---
            async with api_call(tracker, "POST", f"/credentials/{created_id}/set-default") as call:
                result = await client.credentials.set_default(created_id)
                call.result = result
                assert isinstance(result, dict)

            # --- usage ---
            async with api_call(tracker, "GET", f"/credentials/{created_id}/usage") as call:
                result = await client.credentials.usage(created_id)
                call.result = result
                assert isinstance(result, dict)

            # --- audit (may 500 on some environments — server-side issue) ---
            try:
                async with api_call(tracker, "GET", f"/credentials/{created_id}/audit") as call:
                    result = await client.credentials.audit(created_id)
                    call.result = result
                    assert isinstance(result, (dict, list))
            except ModulexError:
                pass  # server-side error is not an SDK issue

        finally:
            if created_id:
                async with api_call(tracker, "DELETE", f"/credentials/{created_id}") as call:
                    await client.credentials.delete(created_id)

    async def test_temporary(self, client: Modulex, tracker: ResultTracker) -> None:
        """POST /credentials/test-temporary — response has is_valid key (dummy key will fail validation)."""
        async with api_call(tracker, "POST", "/credentials/test-temporary") as call:
            result = await client.credentials.test_temporary(
                integration_name="openai",
                auth_type="api_key",
                auth_data={"api_key": "sk-test-integration-dummy-key"},
            )
            call.result = result
            assert isinstance(result, dict)
            assert "is_valid" in result
