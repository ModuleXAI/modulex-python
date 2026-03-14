"""Dashboard-related type definitions."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class LogEntry(TypedDict, total=False):
    """A single audit/activity log entry."""

    id: str
    organization_id: str
    category: str
    operation: str
    performed_by: str
    details: dict[str, Any]
    timestamp: str


class LogsResponse(TypedDict, total=False):
    """Paginated log listing response."""

    success: bool
    organization_id: str
    data: dict[str, Any]
    filters: dict[str, Any]
    meta: dict[str, Any]


class AnalyticsOverviewResponse(TypedDict, total=False):
    """High-level analytics overview for an organization."""

    success: bool
    organization_id: str
    data: dict[str, Any]
    meta: dict[str, Any]


class UserListResponse(TypedDict, total=False):
    """Paginated list of organization members."""

    success: bool
    organization_id: str
    users: list[Any]
    invitation_count: int
    max_seats: int | None
    total: int
    total_pages: int
    current_page: int
    limit: int
    has_next: bool
    has_previous: bool
