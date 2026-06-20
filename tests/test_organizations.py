"""Tests for the Organizations resource (Faz 2 additions)."""

from __future__ import annotations

import json as _json

import httpx
import pytest
import respx

from modulex import Modulex


@pytest.mark.asyncio
class TestOrganizationSettings:
    async def test_preview_invite(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/organizations/invite/preview").mock(
            return_value=httpx.Response(
                200,
                json={"preview_available": True, "interval": "month", "new_quantity": 4, "amount_due": 74.94},
            )
        )
        result = await client.organizations.preview_invite()
        assert result["preview_available"] is True
        assert result["amount_due"] == 74.94

    async def test_get_settings(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/organizations/settings").mock(
            return_value=httpx.Response(200, json={"llm_model_visibility": {}, "composer_llm": None})
        )
        result = await client.organizations.get_settings()
        assert result["composer_llm"] is None

    async def test_set_llm_model_visibility(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.put("/organizations/settings/llm-model-visibility").mock(
            return_value=httpx.Response(200, json={"llm_model_visibility": {"openrouter": [{"id": "m1"}]}})
        )
        await client.organizations.set_llm_model_visibility("openrouter", [{"id": "m1", "display_name": "M1"}])
        sent = _json.loads(route.calls.last.request.content)
        assert sent["integration_name"] == "openrouter"
        assert sent["models"] == [{"id": "m1", "display_name": "M1"}]

    async def test_set_composer_llm(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.put("/organizations/settings/composer-llm").mock(
            return_value=httpx.Response(200, json={"composer_llm": {"integration_name": "openai"}})
        )
        await client.organizations.set_composer_llm("openai", "openai", "gpt-4o-mini", credential_id="cred-1")
        sent = _json.loads(route.calls.last.request.content)
        assert sent == {
            "integration_name": "openai",
            "provider_id": "openai",
            "model_id": "gpt-4o-mini",
            "credential_id": "cred-1",
        }


@pytest.mark.asyncio
class TestOrganizationRoles:
    """Org membership is owner/admin only — the ``member`` role was retired."""

    async def test_invite_defaults_to_admin(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/organizations/invite").mock(
            return_value=httpx.Response(200, json={"success": True, "invitation": {"id": "inv-1", "role": "admin"}})
        )
        await client.organizations.invite("newuser@example.com")
        sent = _json.loads(route.calls.last.request.content)
        assert sent["invited_email"] == "newuser@example.com"
        assert sent["role"] == "admin"  # default is admin, never the retired "member"

    async def test_invite_sends_admin_role(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/organizations/invite").mock(return_value=httpx.Response(200, json={"success": True}))
        await client.organizations.invite("newuser@example.com", role="admin", invitation_message="welcome")
        sent = _json.loads(route.calls.last.request.content)
        assert sent["role"] == "admin"
        assert sent["invitation_message"] == "welcome"

    async def test_update_user_role_sends_admin(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.put("/organizations/org-1/users/user-1/role").mock(
            return_value=httpx.Response(200, json={"success": True, "new_role": "admin"})
        )
        result = await client.organizations.update_user_role("org-1", "user-1", "admin")
        sent = _json.loads(route.calls.last.request.content)
        assert sent == {"role": "admin"}
        assert result["new_role"] == "admin"
