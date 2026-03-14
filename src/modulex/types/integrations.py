"""Integration-related type definitions."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class IntegrationInfo(TypedDict, total=False):
    """Metadata describing a single integration."""

    name: str
    display_name: str
    type: str
    category: str
    description: str | None
    auth_types: list[str]
    icon_url: str | None


class IntegrationBrowseResponse(TypedDict, total=False):
    """Paginated browse response for available integrations."""

    integrations: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
