"""Notification-related response models (Pydantic v2)."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class NotificationItem(ModulexModel):
    """A single notification from GET /notifications.

    The backend returns a heterogeneous union discriminated by
    ``notification_type`` (``"invitation"``, ``"system"`` or
    ``"organization"``). Rather than three rigid shapes, all possible
    fields are modeled as optional so any variant validates; ``id`` is the
    only required field. Unmodeled fields are preserved (``extra="allow"``).

    - invitation: ``notification_type, id, organization_id, organization_name,
      message, created_at, expires_at, role, invited_by_email,
      invitation_message``
    - system: ``notification_type, id, notification_topic, message,
      notification_url, created_at, notified_at, expires_at``
    - organization: ``notification_type, id, organization_id,
      notification_topic, message, notification_url, created_at, notified_at,
      expires_at, is_broadcast``
    """

    id: str
    notification_type: Optional[str] = None
    message: Optional[str] = None
    created_at: Optional[str] = None
    expires_at: Optional[str] = None
    # invitation-specific
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None
    role: Optional[str] = None
    invited_by_email: Optional[str] = None
    invitation_message: Optional[str] = None
    # system / organization-specific
    notification_topic: Optional[str] = None
    notification_url: Optional[str] = None
    notified_at: Optional[str] = None
    is_broadcast: Optional[bool] = None


class NotificationResponse(ModulexModel):
    """Response from GET /notifications."""

    success: bool = True
    notifications: list[NotificationItem] = Field(default_factory=list)
    total: int = 0
    organization_id: Optional[str] = None


class CreatedOrganizationNotification(ModulexModel):
    """The notification object created by POST /notifications/organization."""

    id: str
    organization_id: Optional[str] = None
    notification_topic: Optional[str] = None
    message: Optional[str] = None
    notification_url: Optional[str] = None
    created_at: Optional[str] = None
    notified_at: Optional[str] = None
    expires_at: Optional[str] = None
    is_broadcast: Optional[bool] = None
    notified_to: Optional[str] = None


class CreateOrganizationNotificationResponse(ModulexModel):
    """Response from POST /notifications/organization."""

    success: bool = True
    notification: Optional[CreatedOrganizationNotification] = None
