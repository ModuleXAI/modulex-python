"""Exception classes for the ModuleX SDK."""

from __future__ import annotations

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
    """Raised when rate limited (429)."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = 429,
        response: httpx.Response | None = None,
        body: Any = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response=response, body=body)
        self.retry_after = retry_after


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


_STATUS_CODE_MAP: dict[int, type[ModulexError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionError,
    404: NotFoundError,
    409: ConflictError,
    422: ValidationError,
    429: RateLimitError,
    500: InternalError,
    502: ExternalServiceError,
    503: ServiceUnavailableError,
}

RETRYABLE_STATUS_CODES = {429, 500, 502, 503}


def raise_for_status(response: httpx.Response) -> None:
    """Raise an appropriate exception for error HTTP status codes."""
    if response.status_code < 400:
        return

    try:
        body = response.json()
    except Exception:
        body = {"detail": response.text}

    detail = body.get("detail", response.text) if isinstance(body, dict) else str(body)
    if isinstance(detail, list):
        detail = "; ".join(item.get("msg", str(item)) for item in detail)

    exc_class = _STATUS_CODE_MAP.get(response.status_code, ModulexError)

    kwargs: dict[str, Any] = {
        "status_code": response.status_code,
        "response": response,
        "body": body,
    }

    if exc_class is RateLimitError:
        retry_after_header = response.headers.get("Retry-After")
        retry_after = float(retry_after_header) if retry_after_header else None
        kwargs["retry_after"] = retry_after

    raise exc_class(str(detail), **kwargs)
