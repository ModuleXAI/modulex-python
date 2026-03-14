"""Composer-related type definitions."""

from __future__ import annotations

from typing_extensions import TypedDict


class ComposerChatResponse(TypedDict, total=False):
    """Response from initiating or continuing a composer chat."""

    status: str
    composer_chat_id: str
    workflow_id: str | None
    run_id: str | None
    thread_id: str | None
    stream_url: str | None


class ComposerStatusResponse(TypedDict, total=False):
    """Status snapshot for an active composer session."""

    composer_chat_id: str
    workflow_id: str | None
    is_running: bool
    running_id: str | None
    has_pending_changes: bool
    run_status: str | None
