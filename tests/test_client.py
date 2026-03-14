"""Tests for the Modulex client class."""

from __future__ import annotations

import pytest

from modulex import Modulex
from modulex._config import DEFAULT_BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT


class TestClientInit:
    def test_basic_init(self) -> None:
        client = Modulex(api_key="mx_live_test")
        assert client._config.api_key == "mx_live_test"
        assert client._config.base_url == DEFAULT_BASE_URL
        assert client._config.timeout == DEFAULT_TIMEOUT
        assert client._config.max_retries == DEFAULT_MAX_RETRIES
        assert client._config.organization_id is None

    def test_init_with_all_options(self) -> None:
        client = Modulex(
            api_key="mx_live_test",
            organization_id="org-123",
            base_url="https://custom.api.com",
            timeout=60.0,
            max_retries=5,
        )
        assert client._config.organization_id == "org-123"
        assert client._config.base_url == "https://custom.api.com"
        assert client._config.timeout == 60.0
        assert client._config.max_retries == 5

    def test_base_url_trailing_slash_stripped(self) -> None:
        client = Modulex(api_key="mx_live_test", base_url="https://api.example.com/")
        assert client._config.base_url == "https://api.example.com"

    def test_empty_api_key_raises(self) -> None:
        with pytest.raises(ValueError, match="api_key is required"):
            Modulex(api_key="")


class TestClientContextManager:
    @pytest.mark.asyncio
    async def test_async_context_manager(self) -> None:
        async with Modulex(api_key="mx_live_test") as client:
            assert client._config.api_key == "mx_live_test"

    @pytest.mark.asyncio
    async def test_close(self) -> None:
        client = Modulex(api_key="mx_live_test")
        await client.close()


class TestResourceAccess:
    def test_lazy_resource_creation(self) -> None:
        client = Modulex(api_key="mx_live_test")
        assert client._auth is None
        _ = client.auth
        assert client._auth is not None

    def test_resource_caching(self) -> None:
        client = Modulex(api_key="mx_live_test")
        auth1 = client.auth
        auth2 = client.auth
        assert auth1 is auth2

    def test_all_resources_accessible(self) -> None:
        client = Modulex(api_key="mx_live_test")
        resources = [
            client.auth,
            client.workflows,
            client.executions,
            client.deployments,
            client.chats,
            client.credentials,
            client.integrations,
            client.knowledge,
            client.schedules,
            client.templates,
            client.composer,
            client.dashboard,
            client.subscriptions,
            client.notifications,
            client.api_keys,
            client.system,
            client.organizations,
        ]
        assert len(resources) == 17
        assert all(r is not None for r in resources)
