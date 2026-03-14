"""Notifications resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource


class Notifications(_BaseResource):
    """Resource for listing and creating organization notifications."""

    async def list(self, *, organization_id: str | None = None) -> Any:
        """Return all notifications for the organization."""
        return await self._get("/notifications", organization_id=organization_id)

    async def create(
        self,
        notification_topic: str,
        message: str,
        *,
        notified_to: str | None = None,
        notification_url: str | None = None,
        expires_at: str | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Create and dispatch a new notification to the organization."""
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "notification_topic": notification_topic,
                "message": message,
                "notified_to": notified_to,
                "notification_url": notification_url,
                "expires_at": expires_at,
            }.items()
            if v is not None
        }
        return await self._post("/notifications/organization", json=body, organization_id=organization_id)
