"""Chats resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource
from modulex._streaming import EventSourceStream
from modulex.types.chats import (
    ChatDeleteResponse,
    ChatMessagesListResponse,
    ChatResponse,
)


class Chats(_BaseResource):
    """Resource for managing chat sessions and their messages."""

    async def list(self, *, organization_id: str | None = None) -> dict[str, Any]:
        """Return all chat sessions for the current user or organization.

        The backend groups chats under dynamic folder keys (e.g. ``chats``,
        ``pinned``, ``archived`` plus any user-defined folders), so this stays a
        raw ``dict[str, list[...]]`` rather than a fixed model.
        """
        result: dict[str, Any] = await self._get("/chats", organization_id=organization_id)
        return result

    async def get(self, chat_id: str, *, organization_id: str | None = None) -> ChatResponse:
        """Return a single chat session by its ID."""
        return ChatResponse.model_validate(await self._get(f"/chats/{chat_id}", organization_id=organization_id))

    async def messages(
        self,
        chat_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> ChatMessagesListResponse:
        """Return a paginated list of messages for a chat session."""
        return ChatMessagesListResponse.model_validate(
            await self._get(
                f"/chats/{chat_id}/messages",
                params={"limit": limit, "offset": offset},
                organization_id=organization_id,
            )
        )

    async def update(
        self,
        chat_id: str,
        *,
        title: str | None = None,
        is_private: bool | None = None,
        folder: str | None = None,
        organization_id: str | None = None,
    ) -> ChatResponse:
        """Update metadata for a chat session such as title, privacy, or folder."""
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if is_private is not None:
            body["is_private"] = is_private
        if folder is not None:
            body["folder"] = folder
        return ChatResponse.model_validate(
            await self._patch(f"/chats/{chat_id}", json=body or None, organization_id=organization_id)
        )

    async def delete(self, chat_id: str, *, organization_id: str | None = None) -> ChatDeleteResponse:
        """Delete a chat session by its ID."""
        return ChatDeleteResponse.model_validate(
            await self._delete(f"/chats/{chat_id}", organization_id=organization_id)
        )

    def stream(self, *, organization_id: str | None = None) -> EventSourceStream:
        """Open an SSE stream to receive real-time chat events."""
        return self._stream_sse("/chats/stream", organization_id=organization_id)
