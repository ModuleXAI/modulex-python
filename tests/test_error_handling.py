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

    async def test_429_rate_limit_headers(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/auth/me").mock(
            return_value=httpx.Response(
                429,
                json={"detail": "API key rate limit exceeded"},
                headers={
                    "Retry-After": "5",
                    "X-RateLimit-Limit": "100",
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": "1718800000",
                },
            )
        )
        with pytest.raises(RateLimitError) as exc_info:
            await client.auth.me()
        assert exc_info.value.retry_after == 5.0
        assert exc_info.value.limit == 100
        assert exc_info.value.remaining == 0
        assert exc_info.value.reset == 1718800000.0


@pytest.mark.asyncio
class TestBillingErrors:
    """402/403/429 structured usage-denial envelope: {code, layer, key, current, limit, reason}."""

    async def test_402_payment_required_plain(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        from modulex import PaymentRequiredError

        mock_api.get("/auth/me").mock(return_value=httpx.Response(402, json={"detail": "Payment required"}))
        with pytest.raises(PaymentRequiredError) as exc_info:
            await client.auth.me()
        assert exc_info.value.status_code == 402

    async def test_402_credit_envelope(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        from modulex import CreditExhaustedError

        mock_api.get("/workflows").mock(
            return_value=httpx.Response(
                402,
                json={
                    "code": "credit_plan_exhausted",
                    "layer": "credit",
                    "key": "monthly_credits",
                    "current": 1000,
                    "limit": 1000,
                    "reason": "credit_exhausted",
                },
            )
        )
        with pytest.raises(CreditExhaustedError) as exc_info:
            await client.workflows.list()
        err = exc_info.value
        assert err.code == "credit_plan_exhausted"
        assert err.layer == "credit"
        assert err.current == 1000
        assert err.limit == 1000
        assert err.reason == "credit_exhausted"

    async def test_403_quota_envelope_is_billing_not_permission(
        self, client: Modulex, mock_api: respx.MockRouter
    ) -> None:
        from modulex import QuotaExceededError

        mock_api.get("/workflows").mock(
            return_value=httpx.Response(
                403,
                json={"code": "quota_exceeded", "layer": "quota", "reason": "quota_exceeded"},
            )
        )
        with pytest.raises(QuotaExceededError) as exc_info:
            await client.workflows.list()
        assert exc_info.value.layer == "quota"

    async def test_403_plain_is_still_permission_error(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        # No envelope keys -> regular PermissionError, not a billing error.
        mock_api.get("/workflows").mock(return_value=httpx.Response(403, json={"detail": "Forbidden"}))
        with pytest.raises(PermissionError):
            await client.workflows.list()

    async def test_429_billing_envelope_wrapped_in_detail(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        from modulex import BillingError

        # org-member limiter returns a dict detail envelope
        mock_api.get("/workflows").mock(
            return_value=httpx.Response(
                429,
                json={"detail": {"code": "rate_limit_exceeded", "layer": "rate", "reason": "rate_limit_exceeded"}},
                headers={"Retry-After": "10"},
            )
        )
        with pytest.raises(BillingError) as exc_info:
            await client.workflows.list()
        assert exc_info.value.layer == "rate"
        assert exc_info.value.retry_after == 10.0
