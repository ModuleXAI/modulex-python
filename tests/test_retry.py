"""Tests for retry logic."""

from __future__ import annotations

import httpx
import pytest
import respx

from modulex import Modulex
from modulex._exceptions import InternalError


@pytest.fixture
async def retry_client() -> Modulex:
    c = Modulex(api_key="mx_live_test", organization_id="org-123", max_retries=2)
    yield c  # type: ignore[misc]
    await c.close()


@pytest.mark.asyncio
class TestRetryLogic:
    async def test_retry_on_500(self, retry_client: Modulex) -> None:
        with respx.mock(base_url="https://api.modulex.dev") as mock:
            mock.get("/auth/me").mock(
                side_effect=[
                    httpx.Response(500, json={"detail": "Server error"}),
                    httpx.Response(500, json={"detail": "Server error"}),
                    httpx.Response(200, json={"id": "user-1", "email": "test@example.com"}),
                ]
            )
            result = await retry_client.auth.me()
            assert result["id"] == "user-1"

    async def test_retry_exhausted_raises(self, retry_client: Modulex) -> None:
        with respx.mock(base_url="https://api.modulex.dev") as mock:
            mock.get("/auth/me").mock(return_value=httpx.Response(500, json={"detail": "Server error"}))
            with pytest.raises(InternalError):
                await retry_client.auth.me()

    async def test_no_retry_on_400(self) -> None:
        client = Modulex(api_key="mx_live_test", max_retries=3)
        with respx.mock(base_url="https://api.modulex.dev") as mock:
            route = mock.get("/auth/me").mock(return_value=httpx.Response(400, json={"detail": "Bad request"}))
            with pytest.raises(Exception):
                await client.auth.me()
            assert route.call_count == 1
        await client.close()

    async def test_no_retry_on_401(self) -> None:
        client = Modulex(api_key="mx_live_test", max_retries=3)
        with respx.mock(base_url="https://api.modulex.dev") as mock:
            route = mock.get("/auth/me").mock(return_value=httpx.Response(401, json={"detail": "Unauthorized"}))
            with pytest.raises(Exception):
                await client.auth.me()
            assert route.call_count == 1
        await client.close()

    async def test_no_retry_on_404(self) -> None:
        client = Modulex(api_key="mx_live_test", max_retries=3)
        with respx.mock(base_url="https://api.modulex.dev") as mock:
            route = mock.get("/workflows/missing").mock(return_value=httpx.Response(404, json={"detail": "Not found"}))
            with pytest.raises(Exception):
                await client.workflows.get("missing")
            assert route.call_count == 1
        await client.close()

    async def test_no_retry_on_post(self) -> None:
        client = Modulex(api_key="mx_live_test", max_retries=3)
        with respx.mock(base_url="https://api.modulex.dev") as mock:
            route = mock.post("/workflows").mock(return_value=httpx.Response(500, json={"detail": "Server error"}))
            with pytest.raises(InternalError):
                await client.workflows.create(workflow_schema={})
            assert route.call_count == 1
        await client.close()

    async def test_429_with_retry_after_header(self, retry_client: Modulex) -> None:
        with respx.mock(base_url="https://api.modulex.dev") as mock:
            mock.get("/auth/me").mock(
                side_effect=[
                    httpx.Response(429, json={"detail": "Rate limited"}, headers={"Retry-After": "0.1"}),
                    httpx.Response(200, json={"id": "user-1"}),
                ]
            )
            result = await retry_client.auth.me()
            assert result["id"] == "user-1"
