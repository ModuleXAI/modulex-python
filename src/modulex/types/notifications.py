"""Notification-related type definitions."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class NotificationResponse(TypedDict, total=False):
    """Paginated list of notifications for an organization."""

    success: bool
    notifications: list[Any]
    total: int
    organization_id: str
