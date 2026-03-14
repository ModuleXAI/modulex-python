"""Tests for error handling and exception mapping."""

from __future__ import annotations

import httpx
import pytest
import respx

from modulex import Modulex
from modulex._exceptions import (
    AuthenticationError,
    BadRequestError,
    ConflictError,
    ExternalServiceError,
    InternalError,
    ModulexError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServiceUnavailableError,
    ValidationError,
)


@pytest.mark.asyncio
class TestErrorHandling:
    async def test_400_bad_request(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/auth/me").mock(return_value=httpx.Response(400, json={"detail": "Bad request"}))
        with pytest.raises(BadRequestError) as exc_info:
            await client.auth.me()
        assert exc_info.value.status_code == 400
        assert "Bad request" in exc_info.value.message

    async def test_401_authentication(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/auth/me").mock(return_value=httpx.Response(401, json={"detail": "Invalid API key"}))
        with pytest.raises(AuthenticationError):
            await client.auth.me()

    async def test_403_permission(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/workflows").mock(return_value=httpx.Response(403, json={"detail": "Insufficient permissions"}))
        with pytest.raises(PermissionError):
            await client.workflows.list()

    async def test_404_not_found(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/workflows/missing-id").mock(return_value=httpx.Response(404, json={"detail": "Not found"}))
        with pytest.raises(NotFoundError):
            await client.workflows.get("missing-id")

    async def test_409_conflict(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/workflows").mock(return_value=httpx.Response(409, json={"detail": "Workflow already exists"}))
        with pytest.raises(ConflictError):
            await client.workflows.create(workflow_schema={})

    async def test_422_validation(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/workflows").mock(
            return_value=httpx.Response(
                422,
                json={"detail": [{"loc": ["body", "name"], "msg": "field required", "type": "value_error.missing"}]},
            )
        )
        with pytest.raises(ValidationError):
            await client.workflows.create(workflow_schema={})

    async def test_429_rate_limit(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/auth/me").mock(
            return_value=httpx.Response(
                429,
                json={"detail": "Rate limit exceeded"},
                headers={"Retry-After": "5"},
            )
        )
        with pytest.raises(RateLimitError) as exc_info:
            await client.auth.me()
        assert exc_info.value.retry_after == 5.0

    async def test_500_internal(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/auth/me").mock(return_value=httpx.Response(500, json={"detail": "Internal server error"}))
        with pytest.raises(InternalError):
            await client.auth.me()

    async def test_502_external_service(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/auth/me").mock(return_value=httpx.Response(502, json={"detail": "Bad gateway"}))
        with pytest.raises(ExternalServiceError):
            await client.auth.me()

    async def test_503_service_unavailable(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/auth/me").mock(return_value=httpx.Response(503, json={"detail": "Service unavailable"}))
        with pytest.raises(ServiceUnavailableError):
            await client.auth.me()

    async def test_unknown_error_code(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/auth/me").mock(return_value=httpx.Response(418, json={"detail": "I'm a teapot"}))
        with pytest.raises(ModulexError) as exc_info:
            await client.auth.me()
        assert exc_info.value.status_code == 418

    async def test_error_response_body_preserved(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/auth/me").mock(
            return_value=httpx.Response(400, json={"detail": "Missing field", "code": "MISSING"})
        )
        with pytest.raises(BadRequestError) as exc_info:
            await client.auth.me()
        assert exc_info.value.body is not None
        assert exc_info.value.response is not None

    async def test_non_json_error_response(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/auth/me").mock(return_value=httpx.Response(500, text="Internal Server Error"))
        with pytest.raises(InternalError):
            await client.auth.me()
