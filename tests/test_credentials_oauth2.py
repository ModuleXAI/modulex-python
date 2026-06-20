"""Tests for the Credentials OAuth2 lifecycle (Faz 2 additions)."""

from __future__ import annotations

import json as _json

import httpx
import pytest
import respx

from modulex import Modulex


@pytest.mark.asyncio
class TestCredentialsOAuth2:
    async def test_initiate_oauth2(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/credentials/oauth2/initiate").mock(
            return_value=httpx.Response(200, json={"authorization_url": "https://x/auth", "state": "st"})
        )
        result = await client.credentials.initiate_oauth2(
            "github",
            redirect_uri="https://app/callback",
            scope="repo",
        )
        assert result["authorization_url"] == "https://x/auth"
        sent = _json.loads(route.calls.last.request.content)
        assert sent["integration_name"] == "github"
        assert sent["redirect_uri"] == "https://app/callback"
        assert sent["use_modulex_oauth"] is True
        assert sent["scope"] == "repo"

    async def test_refresh_oauth2(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/credentials/cred-1/oauth2/refresh").mock(
            return_value=httpx.Response(200, json={"credential_id": "cred-1", "auth_type": "oauth2"})
        )
        result = await client.credentials.refresh_oauth2("cred-1")
        assert result["credential_id"] == "cred-1"

    async def test_create_passes_oauth_config(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/credentials").mock(
            return_value=httpx.Response(200, json={"credential_id": "cred-2", "auth_type": "oauth2"})
        )
        await client.credentials.create(
            "github",
            auth_data={"access_token": "tok"},
            oauth_config={"client_id": "cid", "client_secret": "secret"},
        )
        sent = _json.loads(route.calls.last.request.content)
        assert sent["oauth_config"] == {"client_id": "cid", "client_secret": "secret"}
        assert sent["auth_data"] == {"access_token": "tok"}
