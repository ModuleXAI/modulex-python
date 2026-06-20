"""Exception classes for the ModuleX SDK."""

from __future__ import annotations

from email.utils import parsedate_to_datetime
from typing import Any

import httpx


class ModulexError(Exception):
    """Base exception for all ModuleX SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response: httpx.Response | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response
        self.body = body


class AuthenticationError(ModulexError):
    """Raised when authentication fails (401)."""


class PermissionError(ModulexError):
    """Raised when the user lacks permissions (403)."""


class NotFoundError(ModulexError):
    """Raised when a resource is not found (404)."""


class BadRequestError(ModulexError):
    """Raised for malformed requests (400)."""


class ValidationError(ModulexError):
    """Raised for validation errors (422)."""


class ConflictError(ModulexError):
    """Raised for resource conflicts (409)."""


class RateLimitError(ModulexError):
    """Raised when rate limited (429).

    Carries the rate-limit headers the backend sends (``X-RateLimit-*`` and
    ``Retry-After``) so callers can back off intelligently.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = 429,
        response: httpx.Response | None = None,
        body: Any = None,
        retry_after: float | None = None,
        limit: int | None = None,
        remaining: int | None = None,
        reset: float | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response=response, body=body)
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
        self.reset = reset


class InternalError(ModulexError):
    """Raised for internal server errors (500)."""


class ExternalServiceError(ModulexError):
    """Raised for external service errors (502)."""


class ServiceUnavailableError(ModulexError):
    """Raised when the service is unavailable (503)."""


class StreamError(ModulexError):
    """Raised for SSE stream errors."""


class TimeoutError(ModulexError):
    """Raised when a request times out."""


class BillingError(ModulexError):
    """Base class for billing / quota / credit / wallet denials.

    The ModuleX backend returns a *structured denial envelope* (top-level, NOT
    under ``detail``) for usage gating: ``{code, layer, key, current, limit, reason}``.
    The ``layer`` determines the HTTP status (quota -> 403, rate -> 429,
    credit/wallet -> 402). This class surfaces those fields structurally instead
    of collapsing them into an opaque message.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response: httpx.Response | None = None,
        body: Any = None,
        code: str | None = None,
        layer: str | None = None,
        key: str | None = None,
        current: float | int | None = None,
        limit: float | int | None = None,
        reason: str | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response=response, body=body)
        self.code = code
        self.layer = layer
        self.key = key
        self.current = current
        self.limit = limit
        self.reason = reason
        self.retry_after = retry_after


class PaymentRequiredError(BillingError):
    """Raised for payment-required denials (402) without a structured envelope."""


class QuotaExceededError(BillingError):
    """Raised when a usage quota is exceeded (layer="quota", HTTP 403)."""


class CreditExhaustedError(BillingError):
    """Raised when the credit plan is exhausted (layer="credit", HTTP 402)."""


class WalletError(BillingError):
    """Raised for wallet overage denials (layer="wallet", HTTP 402)."""


_STATUS_CODE_MAP: dict[int, type[ModulexError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    402: PaymentRequiredError,
    403: PermissionError,
    404: NotFoundError,
    409: ConflictError,
    422: ValidationError,
    429: RateLimitError,
    500: InternalError,
    502: ExternalServiceError,
    503: ServiceUnavailableError,
}

# Map the backend denial ``layer`` to a specific BillingError subclass.
_BILLING_LAYER_MAP: dict[str, type[BillingError]] = {
    "quota": QuotaExceededError,
    "credit": CreditExhaustedError,
    "wallet": WalletError,
}

RETRYABLE_STATUS_CODES = {429, 500, 502, 503}

# Statuses that may carry a structured billing/usage denial envelope.
_DENIAL_STATUSES = {402, 403, 429}
_DENIAL_KEYS = ("code", "layer", "reason")


def parse_retry_after(value: str | None) -> float | None:
    """Parse a ``Retry-After`` header (delay-seconds OR an HTTP-date)."""
    if not value:
        return None
    value = value.strip()
    try:
        return float(value)
    except ValueError:
        pass
    try:
        from datetime import datetime, timezone

        dt = parsedate_to_datetime(value)
        if dt is None:
            return None
        delta = (dt - datetime.now(timezone.utc)).total_seconds()
        return max(delta, 0.0)
    except (TypeError, ValueError):
        return None


def _parse_rate_headers(response: httpx.Response) -> tuple[int | None, int | None, float | None]:
    """Read ``X-RateLimit-Limit/Remaining/Reset`` headers (best-effort)."""

    def _as_int(name: str) -> int | None:
        raw = response.headers.get(name)
        try:
            return int(raw) if raw is not None else None
        except ValueError:
            return None

    reset_raw = response.headers.get("X-RateLimit-Reset")
    try:
        reset = float(reset_raw) if reset_raw is not None else None
    except ValueError:
        reset = None
    return _as_int("X-RateLimit-Limit"), _as_int("X-RateLimit-Remaining"), reset


def _extract_denial_envelope(body: Any) -> dict[str, Any] | None:
    """Return the structured denial envelope if present.

    Tolerates three shapes (mirrors the UI's ``billing-error.ts:extractEnvelope``):
      - top-level ``{code, layer, ...}``
      - ``{"detail": {code, layer, ...}}`` (FastAPI-wrapped dict detail)
      - a bare ``{"reason": ...}`` top-level dict
    """
    candidates = []
    if isinstance(body, dict):
        candidates.append(body)
        detail = body.get("detail")
        if isinstance(detail, dict):
            candidates.append(detail)
    for candidate in candidates:
        if any(k in candidate for k in _DENIAL_KEYS):
            return candidate
    return None


def raise_for_status(response: httpx.Response) -> None:
    """Raise an appropriate exception for error HTTP status codes."""
    if response.status_code < 400:
        return

    try:
        body = response.json()
    except Exception:
        body = {"detail": response.text}

    status = response.status_code

    # 1) Structured billing/usage denial envelope (402/403/429) — surface fields.
    if status in _DENIAL_STATUSES:
        envelope = _extract_denial_envelope(body)
        if envelope is not None:
            layer = envelope.get("layer")
            reason = envelope.get("reason")
            code = envelope.get("code")
            message = reason or code or "Request denied by usage gate"
            retry_after = parse_retry_after(response.headers.get("Retry-After"))
            exc_cls = _BILLING_LAYER_MAP.get(layer or "", BillingError)
            raise exc_cls(
                str(message),
                status_code=status,
                response=response,
                body=body,
                code=code,
                layer=layer,
                key=envelope.get("key"),
                current=envelope.get("current"),
                limit=envelope.get("limit"),
                reason=reason,
                retry_after=retry_after,
            )

    # 2) Standard error mapping.
    detail = body.get("detail", response.text) if isinstance(body, dict) else str(body)
    if isinstance(detail, list):  # FastAPI 422 validation errors
        detail = "; ".join(item.get("msg", str(item)) if isinstance(item, dict) else str(item) for item in detail)
    elif isinstance(detail, dict):  # org-member 429 dict-detail (non-envelope)
        detail = detail.get("reason") or detail.get("message") or detail.get("code") or str(detail)

    exc_class = _STATUS_CODE_MAP.get(status, ModulexError)

    kwargs: dict[str, Any] = {
        "status_code": status,
        "response": response,
        "body": body,
    }

    if exc_class is RateLimitError:
        kwargs["retry_after"] = parse_retry_after(response.headers.get("Retry-After"))
        limit, remaining, reset = _parse_rate_headers(response)
        kwargs["limit"] = limit
        kwargs["remaining"] = remaining
        kwargs["reset"] = reset

    raise exc_class(str(detail), **kwargs)
