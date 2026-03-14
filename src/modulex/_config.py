"""Client configuration for the ModuleX SDK."""

from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_BASE_URL = "https://api.modulex.dev"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3


@dataclass
class ClientConfig:
    """Configuration for the ModuleX client."""

    api_key: str
    organization_id: str | None = None
    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    default_headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        if not self.api_key:
            raise ValueError("api_key is required")
