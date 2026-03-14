"""Chat-related type definitions."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class ChatResponse(TypedDict, total=False):
    """Response representing a chat session."""

    id: str
    organization_id: str
    creator_id: str
    title: str | None
    is_private: bool
    running_id: str | None
    messages: list[Any]
    created_at: str
    updated_at: str
    deleted_at: str | None


class ChatMessageResponse(TypedDict, total=False):
    """Response representing a single chat message."""

    id: str
    chat_id: str
    role: str
    content: Any
    workflow: dict[str, Any]
    run_id: str | None
    running_status: str | None
    created_at: str
    updated_at: str


class ChatListResponse(TypedDict, total=False):
    """Categorized list of chats for the current user."""

    chats: list[Any]
    pinned: list[Any]
    archived: list[Any]


class ChatMessagesListResponse(TypedDict, total=False):
    """Paginated list of messages within a chat."""

    messages: list[Any]
    total: int
    limit: int
    offset: int
    has_next: bool
    actual_count: int
