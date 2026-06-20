"""Composer-related response models (Pydantic v2).

Mirrors the backend ``app/api/composer.py`` response bodies for the AI-assisted
workflow composer and its human-in-the-loop (HITL) chat sessions. The HITL
wire-contract types (``UserInputRequest`` / ``UserInputResponse`` and the
``ComposerLLMConfig``) live in :mod:`modulex.types.realtime`; import them from
there rather than redefining them.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class ComposerChatResponse(ModulexModel):
    """Response from POST /composer/chat (initiate or continue a run)."""

    status: Optional[str] = None
    composer_chat_id: Optional[str] = None
    workflow_id: Optional[str] = None
    run_id: Optional[str] = None
    thread_id: Optional[str] = None
    stream_url: Optional[str] = None


class ComposerChatMessage(ModulexModel):
    """A single message inside a composer chat detail (GET /composer/chat/{id})."""

    id: str
    role: Optional[str] = None
    content: Optional[Any] = None
    thinking: Optional[Any] = None
    workflow_changes: Optional[Any] = None
    run_id: Optional[str] = None
    running_status: Optional[str] = None
    created_at: Optional[str] = None


class ComposerChatDetails(ModulexModel):
    """Response from GET /composer/chat/{composer_chat_id}."""

    id: str
    workflow_id: Optional[str] = None
    touched_workflow_ids: list[str] = Field(default_factory=list)
    title: Optional[str] = None
    running_id: Optional[str] = None
    has_pending_changes: bool = False
    pending_user_input_request: Optional[dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    messages: list[ComposerChatMessage] = Field(default_factory=list)


class ComposerChatListItem(ModulexModel):
    """An item in the user-scoped composer chat list (GET /composer/chats)."""

    id: str
    workflow_id: Optional[str] = None
    title: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_running: bool = False


class ComposerChatListResponse(ModulexModel):
    """Response from GET /composer/chats (cursor-paginated)."""

    items: list[ComposerChatListItem] = Field(default_factory=list)
    next_cursor: Optional[str] = None


class ComposerFocusResponse(ModulexModel):
    """Response from PATCH /composer/chat/{composer_chat_id}/focus."""

    composer_chat_id: Optional[str] = None
    workflow_id: Optional[str] = None
    updated_at: Optional[str] = None


class WorkflowSyncData(ModulexModel):
    """Canvas-sync payload returned by save/revert (``workflow_sync`` field)."""

    workflow_id: Optional[str] = None
    edit_version: Optional[Any] = None
    workflow: Optional[dict[str, Any]] = None
    input: Optional[dict[str, Any]] = None


class ComposerSaveResponse(ModulexModel):
    """Response from POST /composer/chat/{composer_chat_id}/save."""

    status: Optional[str] = None
    workflow_id: Optional[str] = None
    workflow_name: Optional[str] = None
    message: Optional[str] = None
    workflow_sync: Optional[WorkflowSyncData] = None


class ComposerRevertResponse(ModulexModel):
    """Response from POST /composer/chat/{composer_chat_id}/revert."""

    status: Optional[str] = None
    workflow_id: Optional[str] = None
    workflow_name: Optional[str] = None
    message: Optional[str] = None
    workflow_sync: Optional[WorkflowSyncData] = None


class ComposerResumeResponse(ModulexModel):
    """Response from POST /composer/chat/{composer_chat_id}/resume.

    A resume produces a NEW ``run_id``; re-subscribe with ``listen`` on it.
    """

    status: Optional[str] = None
    composer_chat_id: Optional[str] = None
    run_id: Optional[str] = None
    thread_id: Optional[str] = None
    stream_url: Optional[str] = None


class ComposerStatusResponse(ModulexModel):
    """Response from GET /composer/chat/{composer_chat_id}/status."""

    composer_chat_id: Optional[str] = None
    workflow_id: Optional[str] = None
    is_running: bool = False
    awaiting_input: bool = False
    pending_request_id: Optional[str] = None
    running_id: Optional[str] = None
    has_pending_changes: bool = False
    run_status: Optional[dict[str, Any]] = None


class ComposerCancelResponse(ModulexModel):
    """Response from POST /composer/chat/{composer_chat_id}/cancel."""

    status: Optional[str] = None
    composer_chat_id: Optional[str] = None
    run_id: Optional[str] = None


class ComposerDeleteResponse(ModulexModel):
    """Response from DELETE /composer/chat/{composer_chat_id}."""

    status: Optional[str] = None
    composer_chat_id: Optional[str] = None
    permanent: bool = False
