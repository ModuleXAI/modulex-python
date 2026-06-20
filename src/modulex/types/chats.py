"""Chat-related response models (Pydantic v2)."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class ChatMessageResponse(ModulexModel):
    """A single chat message (GET /chats/{chat_id}/messages item).

    ``content`` is intentionally loose (backend returns ``Union[str, Dict,
    List[Dict]]``).
    """

    id: str
    chat_id: Optional[str] = None
    role: Optional[str] = None
    content: Any = None
    workflow: Optional[dict[str, Any]] = None
    run_id: Optional[str] = None
    running_status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None


class ChatResponse(ModulexModel):
    """A chat session (GET /chats/{chat_id}, PATCH /chats/{chat_id}).

    ``messages`` is populated on GET by id (``load_messages=True``) and is
    ``None`` on PATCH.
    """

    id: str
    organization_id: Optional[str] = None
    creator_id: Optional[str] = None
    title: Optional[str] = None
    is_private: bool = False
    running_id: Optional[str] = None
    messages: Optional[list[ChatMessageResponse]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None


class ChatListItem(ModulexModel):
    """A lightweight chat entry inside a folder group (GET /chats item).

    Backend ``ChatListItem`` omits ``organization_id``, ``messages`` and
    ``deleted_at`` (those exist only on the full ``ChatResponse``).
    """

    id: str
    title: Optional[str] = None
    creator_id: Optional[str] = None
    is_private: bool = False
    running_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ChatMessagesListResponse(ModulexModel):
    """Paginated list of messages within a chat (GET /chats/{chat_id}/messages).

    Backend ``MessageListResponse`` returns only ``messages``, ``limit`` and
    ``offset`` (the previously declared ``total``/``has_next``/``actual_count``
    fields were stale and are not returned).
    """

    messages: list[ChatMessageResponse] = Field(default_factory=list)
    limit: Optional[int] = None
    offset: int = 0


class ChatDeleteResponse(ModulexModel):
    """Response from DELETE /chats/{chat_id}."""

    success: bool = True
    message: Optional[str] = None
