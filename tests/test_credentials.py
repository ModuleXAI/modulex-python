"""Tests for the Credentials resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from modulex import Modulex


@pytest.mark.asyncio
class TestCredentials:
    async def test_list(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/credentials").mock(
            return_value=httpx.Response(
                200,
                json={
                    "integrations": {"openai": {"total_count": 1, "credentials": []}},
                    "total_credentials": 1,
                },
            )
        )
        result = await client.credentials.list()
        assert result["total_credentials"] == 1

    async def test_list_by_integration(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.get("/credentials").mock(
            return_value=httpx.Response(200, json={"credentials": [], "total_count": 0})
        )
        await client.credentials.list(integration_name="openai")
        assert route.calls.last.request.url.params.get("integration_name") == "openai"

    async def test_get(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/credentials/cred-123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "credential_id": "cred-123",
                    "integration_name": "openai",
                    "auth_type": "api_key",
                },
            )
        )
        result = await client.credentials.get("cred-123")
        assert result["credential_id"] == "cred-123"

    async def test_create(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/credentials").mock(
            return_value=httpx.Response(
                201,
                json={
                    "credential_id": "cred-new",
                    "integration_name": "openai",
                },
            )
        )
        result = await client.credentials.create(
            integration_name="openai",
            auth_data={"api_key": "sk-test"},
            display_name="Test Key",
        )
        assert result["credential_id"] == "cred-new"

    async def test_delete(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.delete("/credentials/cred-123").mock(return_value=httpx.Response(204))
        result = await client.credentials.delete("cred-123")
        assert result is None

    async def test_set_default(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/credentials/cred-123/set-default").mock(
            return_value=httpx.Response(200, json={"credential_id": "cred-123", "is_default": True})
        )
        result = await client.credentials.set_default("cred-123")
        assert result["is_default"] is True

    async def test_test_credential(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/credentials/cred-123/test").mock(
            return_value=httpx.Response(
                200,
                json={
                    "credential_id": "cred-123",
                    "is_valid": True,
                    "message": "Connection successful",
                },
            )
        )
        result = await client.credentials.test("cred-123")
        assert result["is_valid"] is True

    async def test_test_temporary(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/credentials/test-temporary").mock(
            return_value=httpx.Response(
                200,
                json={
                    "is_valid": True,
                    "message": "Valid",
                },
            )
        )
        result = await client.credentials.test_temporary(
            integration_name="openai",
            auth_type="api_key",
            auth_data={"api_key": "sk-test"},
        )
        assert result["is_valid"] is True

    async def test_create_mcp_server(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/credentials/mcp-server").mock(
            return_value=httpx.Response(
                200,
                json={
                    "credential_id": "mcp-cred",
                    "integration_name": "mcp_server",
                },
            )
        )
        result = await client.credentials.create_mcp_server(
            server_url="https://mcp-server.example.com",
        )
        assert result["credential_id"] == "mcp-cred"
