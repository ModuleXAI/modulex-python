"""Shared test fixtures for the ModuleX SDK tests."""

from __future__ import annotations

import pytest

from modulex import Modulex

try:
    import respx

    HAS_RESPX = True
except ModuleNotFoundError:
    HAS_RESPX = False


@pytest.fixture
def base_url() -> str:
    return "https://api.modulex.dev"


@pytest.fixture
def api_key() -> str:
    return "mx_live_test_key_123"


@pytest.fixture
def org_id() -> str:
    return "org-test-uuid-123"


@pytest.fixture
async def client(api_key: str, org_id: str, base_url: str) -> Modulex:
    c = Modulex(api_key=api_key, organization_id=org_id, base_url=base_url, max_retries=0)
    yield c  # type: ignore[misc]
    await c.close()


if HAS_RESPX:

    @pytest.fixture
    def mock_api(base_url: str) -> respx.MockRouter:  # type: ignore[name-defined]
        with respx.mock(base_url=base_url) as router:  # type: ignore[name-defined]
            yield router
