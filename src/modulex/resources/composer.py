"""Composer resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource
from modulex._streaming import EventSourceStream
from modulex.types.composer import (
    ComposerCancelResponse,
    ComposerChatDetails,
    ComposerChatListResponse,
    ComposerChatResponse,
    ComposerDeleteResponse,
    ComposerFocusResponse,
    ComposerResumeResponse,
    ComposerRevertResponse,
    ComposerSaveResponse,
    ComposerStatusResponse,
)
from modulex.types.realtime import ComposerLLMConfig, UserInputResponse, _to_payload


class Composer(_BaseResource):
    """Resource for the AI-assisted workflow composer and its chat sessions."""

    async def chat(
        self,
        message: str,
        *,
        workflow_id: str | None = None,
        composer_chat_id: str | None = None,
        llm: ComposerLLMConfig | dict[str, Any] | None = None,
        organization_id: str | None = None,
    ) -> ComposerChatResponse:
        """Send a message to the composer and receive an AI-generated workflow response.

        ``llm`` is a provider config ({integration_name, provider_id, model_id,
        credential_id?}); pass a :class:`ComposerLLMConfig` or an equivalent dict.
        Omit it to use the organization's default composer LLM.
        """
        body: dict[str, Any] = {"message": message}
        if workflow_id is not None:
            body["workflow_id"] = workflow_id
        if composer_chat_id is not None:
            body["composer_chat_id"] = composer_chat_id
        if llm is not None:
            body["llm"] = _to_payload(llm)
        return ComposerChatResponse.model_validate(
            await self._post("/composer/chat", json=body, organization_id=organization_id)
        )

    async def get(
        self,
        composer_chat_id: str,
        *,
        organization_id: str | None = None,
    ) -> ComposerChatDetails:
        """Return a composer chat session by its ID."""
        return ComposerChatDetails.model_validate(
            await self._get(f"/composer/chat/{composer_chat_id}", organization_id=organization_id)
        )

    async def list(
        self,
        *,
        limit: int = 20,
        cursor: str | None = None,
        organization_id: str | None = None,
    ) -> ComposerChatListResponse:
        """List the caller's composer chats (newest first, cursor-paginated).

        ``cursor`` is the ``updated_at`` ISO timestamp of the previous page's last
        item; the response ``next_cursor`` is non-null only when more pages exist.
        """
        params: dict[str, Any] = {"limit": limit, "cursor": cursor}
        return ComposerChatListResponse.model_validate(
            await self._get("/composer/chats", params=params, organization_id=organization_id)
        )

    def listen(
        self,
        composer_chat_id: str,
        run_id: str,
        *,
        organization_id: str | None = None,
    ) -> EventSourceStream:
        """Open an SSE stream to receive live events for a composer chat run.

        Event types are carried in ``event.event`` (normalized from ``data['type']``).
        A ``user_input_request`` event means the run paused for HITL input — answer
        it with :meth:`resume`. See :data:`modulex.types.realtime.COMPOSER_EVENT_TYPES`.
        """
        return self._stream_sse(
            f"/composer/chat/{composer_chat_id}/listen/{run_id}",
            organization_id=organization_id,
        )

    async def resume(
        self,
        composer_chat_id: str,
        *,
        request_id: str,
        response: UserInputResponse | dict[str, Any],
        llm: ComposerLLMConfig | dict[str, Any] | None = None,
        organization_id: str | None = None,
    ) -> ComposerResumeResponse:
        """Resume a composer run paused on a HITL ``user_input_request``.

        ``request_id`` is the paused question's id (from the ``user_input_request``
        event). ``response`` is a :data:`UserInputResponse` (or equivalent dict).
        ``llm`` is required in production (the executor rebuilds the chat model on
        resume); pass the same config used in :meth:`chat`. Returns a NEW ``run_id``;
        re-subscribe with :meth:`listen` on that run.
        """
        body: dict[str, Any] = {
            "request_id": request_id,
            "response": _to_payload(response),
            "llm": _to_payload(llm) if llm is not None else None,
        }
        return ComposerResumeResponse.model_validate(
            await self._post(
                f"/composer/chat/{composer_chat_id}/resume",
                json=body,
                organization_id=organization_id,
            )
        )

    async def set_focus(
        self,
        composer_chat_id: str,
        workflow_id: str | None,
        *,
        organization_id: str | None = None,
    ) -> ComposerFocusResponse:
        """Set (or clear) a composer chat's focused workflow.

        Pass ``None`` to unfocus. The ``workflow_id`` key is always sent (the
        backend requires its presence; ``null`` means unfocus).
        """
        return ComposerFocusResponse.model_validate(
            await self._patch(
                f"/composer/chat/{composer_chat_id}/focus",
                json={"workflow_id": workflow_id},
                organization_id=organization_id,
            )
        )

    async def save(
        self,
        composer_chat_id: str,
        *,
        workflow_id: str | None = None,
        organization_id: str | None = None,
    ) -> ComposerSaveResponse:
        """Save the workflow state generated by a composer chat session.

        ``workflow_id`` targets a specific touched workflow; omit it to use the
        chat's focused workflow (required if the chat is unfocused).
        """
        body: dict[str, Any] = {"workflow_id": workflow_id} if workflow_id else {}
        return ComposerSaveResponse.model_validate(
            await self._post(
                f"/composer/chat/{composer_chat_id}/save",
                json=body or None,
                organization_id=organization_id,
            )
        )

    async def revert(
        self,
        composer_chat_id: str,
        *,
        workflow_id: str | None = None,
        organization_id: str | None = None,
    ) -> ComposerRevertResponse:
        """Revert the composer chat session to its last saved workflow state."""
        body: dict[str, Any] = {"workflow_id": workflow_id} if workflow_id else {}
        return ComposerRevertResponse.model_validate(
            await self._post(
                f"/composer/chat/{composer_chat_id}/revert",
                json=body or None,
                organization_id=organization_id,
            )
        )

    async def delete(
        self,
        composer_chat_id: str,
        *,
        permanent: bool = False,
        organization_id: str | None = None,
    ) -> ComposerDeleteResponse:
        """Delete a composer chat session, optionally removing it permanently."""
        params: dict[str, Any] = {"permanent": permanent}
        return ComposerDeleteResponse.model_validate(
            await self._delete(
                f"/composer/chat/{composer_chat_id}",
                params=params,
                organization_id=organization_id,
            )
        )

    async def status(
        self,
        composer_chat_id: str,
        *,
        organization_id: str | None = None,
    ) -> ComposerStatusResponse:
        """Return the current processing status of a composer chat session."""
        return ComposerStatusResponse.model_validate(
            await self._get(
                f"/composer/chat/{composer_chat_id}/status",
                organization_id=organization_id,
            )
        )

    async def cancel(
        self,
        composer_chat_id: str,
        *,
        organization_id: str | None = None,
    ) -> ComposerCancelResponse:
        """Cancel an in-progress composer chat run."""
        return ComposerCancelResponse.model_validate(
            await self._post(
                f"/composer/chat/{composer_chat_id}/cancel",
                organization_id=organization_id,
            )
        )
