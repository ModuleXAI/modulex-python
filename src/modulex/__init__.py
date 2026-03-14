"""ModuleX Python SDK — Official client for the ModuleX AI workflow orchestration platform."""

from modulex._client import Modulex
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
    StreamError,
    TimeoutError,
    ValidationError,
)
from modulex._streaming import SSEEvent

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
    "SSEEvent",
]

__version__ = "0.1.0"
