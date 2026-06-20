"""Assistant (agentic standard chat) response models (Pydantic v2).

Mirrors the backend ``app/api/assistant.py`` response bodies. The assistant
shares the HITL wire contract with the composer: the ``ComposerLLMConfig`` and
the ``UserInputRequest`` / ``UserInputResponse`` discriminated unions live in
:mod:`modulex.types.realtime`; import them from there rather than redefining
them. These models describe the assistant's response envelopes only.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class AssistantChatResponse(ModulexModel):
    """Response from POST /assistant/chat (start or continue a run)."""

    status: Optional[str] = None
    chat_id: Optional[str] = None
    run_id: Optional[str] = None
    thread_id: Optional[str] = None
    stream_url: Optional[str] = None


class AssistantResumeResponse(ModulexModel):
    """Response from POST /assistant/chat/{id}/resume (carries a NEW run_id)."""

    status: Optional[str] = None
    chat_id: Optional[str] = None
    run_id: Optional[str] = None
    thread_id: Optional[str] = None
    stream_url: Optional[str] = None


class AssistantMessage(ModulexModel):
    """A single message inside an assistant chat (GET /assistant/chat/{id})."""

    id: str
    role: Optional[str] = None
    content: Optional[Any] = None
    thinking: Optional[Any] = None
    run_id: Optional[str] = None
    running_status: Optional[str] = None
    created_at: Optional[str] = None


class AssistantChatDetails(ModulexModel):
    """Response from GET /assistant/chat/{id}."""

    id: str
    title: Optional[str] = None
    running_id: Optional[str] = None
    pending_user_input_request: Optional[dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    messages: list[AssistantMessage] = Field(default_factory=list)


class AssistantChatListItem(ModulexModel):
    """An item in the user-scoped assistant chat list (GET /assistant/chats)."""

    id: str
    title: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_running: bool = False


class AssistantChatListResponse(ModulexModel):
    """Response from GET /assistant/chats (cursor-paginated)."""

    items: list[AssistantChatListItem] = Field(default_factory=list)
    next_cursor: Optional[str] = None


class AssistantStatusResponse(ModulexModel):
    """Response from GET /assistant/chat/{id}/status."""

    chat_id: Optional[str] = None
    is_running: bool = False
    awaiting_input: bool = False
    pending_request_id: Optional[str] = None
    running_id: Optional[str] = None
    run_status: Optional[dict[str, Any]] = None


class AssistantCancelResponse(ModulexModel):
    """Response from POST /assistant/chat/{id}/cancel."""

    status: Optional[str] = None
    chat_id: Optional[str] = None
    run_id: Optional[str] = None


class AssistantDeleteResponse(ModulexModel):
    """Response from DELETE /assistant/chat/{id}."""

    status: Optional[str] = None
    chat_id: Optional[str] = None
    permanent: bool = False
