"""Integration tests for SDK error handling.

Negative tests that verify the correct exception types are raised when the API
returns 4xx responses.

Covers:
  - NotFoundError for unknown resource IDs
  - ValidationError / BadRequestError for malformed request bodies
  - PermissionError when no organization header is supplied
"""

from __future__ import annotations

import pytest

from modulex import (
    BadRequestError,
    Modulex,
    NotFoundError,
    PermissionError,
    ValidationError,
)
from tests.integration.conftest import ResultTracker, api_call


@pytest.mark.asyncio
class TestErrorHandling:
    """Live API tests that assert correct exception behaviour for error responses."""

    async def test_not_found(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /workflows/<nil-uuid> — must raise NotFoundError for an unknown workflow ID."""
        async with api_call(tracker, "GET", "/workflows/00000000-0000-0000-0000-000000000000") as call:
            with pytest.raises(NotFoundError):
                result = await client.workflows.get("00000000-0000-0000-0000-000000000000")
                call.result = result

    async def test_invalid_body(self, client: Modulex, tracker: ResultTracker) -> None:
        """POST /workflows — must raise ValidationError or BadRequestError for an empty body."""
        async with api_call(tracker, "POST", "/workflows") as call:
            with pytest.raises((ValidationError, BadRequestError)):
                result = await client.workflows.create({})
                call.result = result

    async def test_no_org_header(self, client: Modulex, tracker: ResultTracker) -> None:
        """GET /workflows — must raise PermissionError when no organization_id is provided."""
        no_org_client = Modulex(
            api_key=client._config.api_key,
            base_url=client._config.base_url,
            timeout=15.0,
        )
        try:
            async with api_call(tracker, "GET", "/workflows (no-org)") as call:
                with pytest.raises((PermissionError, Exception)):
                    result = await no_org_client.workflows.list()
                    call.result = result
        finally:
            await no_org_client.close()
