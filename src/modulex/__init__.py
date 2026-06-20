"""ModuleX Python SDK — Official client for the ModuleX AI workflow orchestration platform."""

from modulex._client import Modulex
from modulex._exceptions import (
    AuthenticationError,
    BadRequestError,
    BillingError,
    ConflictError,
    CreditExhaustedError,
    ExternalServiceError,
    InternalError,
    ModulexError,
    NotFoundError,
    PaymentRequiredError,
    PermissionError,
    QuotaExceededError,
    RateLimitError,
    ServiceUnavailableError,
    StreamError,
    TimeoutError,
    ValidationError,
    WalletError,
)
from modulex._streaming import SSEEvent
from modulex._version import __version__

__all__ = [
    "Modulex",
    "ModulexError",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "BadRequestError",
    "ValidationError",
    "ConflictError",
    "RateLimitError",
    "InternalError",
    "ExternalServiceError",
    "ServiceUnavailableError",
    "StreamError",
    "TimeoutError",
    "BillingError",
    "PaymentRequiredError",
    "QuotaExceededError",
    "CreditExhaustedError",
    "WalletError",
    "SSEEvent",
    "__version__",
]
