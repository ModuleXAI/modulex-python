"""Assistant resource for the ModuleX Python SDK.

The assistant is the agentic "standard chat" surface. It shares the HITL
(human-in-the-loop) contract with the composer: a paused run emits a
``user_input_request`` SSE event answered via :meth:`resume`.
"""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource
from modulex._streaming import EventSourceStream
from modulex.types.assistant import (
    AssistantCancelResponse,
    AssistantChatDetails,
    AssistantChatListResponse,
    AssistantChatResponse,
    AssistantDeleteResponse,
    AssistantResumeResponse,
    AssistantStatusResponse,
)
from modulex.types.realtime import ComposerLLMConfig, UserInputResponse, _to_payload


class Assistant(_BaseResource):
    """Resource for the agentic assistant chat (all endpoints: org member access)."""

    async def chat(
        self,
        message: str,
        *,
        chat_id: str | None = None,
        llm: ComposerLLMConfig | dict[str, Any] | None = None,
        organization_id: str | None = None,
    ) -> AssistantChatResponse:
        """Start a new assistant chat or continue an existing one.

        ``llm`` is a provider config ({integration_name, provider_id, model_id,
        credential_id?}); omit it to use the organization's default. Returns a
        ``run_id`` — open the event stream with :meth:`listen`.
        """
        body: dict[str, Any] = {"message": message}
        if chat_id is not None:
            body["chat_id"] = chat_id
        if llm is not None:
            body["llm"] = _to_payload(llm)
        return AssistantChatResponse.model_validate(
            await self._post("/assistant/chat", json=body, organization_id=organization_id)
        )

    async def get(self, chat_id: str, *, organization_id: str | None = None) -> AssistantChatDetails:
        """Return an assistant chat with all its messages (and any pending HITL question)."""
        return AssistantChatDetails.model_validate(
            await self._get(f"/assistant/chat/{chat_id}", organization_id=organization_id)
        )

    async def list(
        self,
        *,
        limit: int = 20,
        cursor: str | None = None,
        organization_id: str | None = None,
    ) -> AssistantChatListResponse:
        """List the caller's assistant chats (newest first, cursor-paginated)."""
        params: dict[str, Any] = {"limit": limit, "cursor": cursor}
        return AssistantChatListResponse.model_validate(
            await self._get("/assistant/chats", params=params, organization_id=organization_id)
        )

    def listen(
        self,
        chat_id: str,
        run_id: str,
        *,
        organization_id: str | None = None,
    ) -> EventSourceStream:
        """Open an SSE stream of live events for an assistant run.

        Event types are carried in ``event.event`` (normalized from ``data['type']``).
        A ``user_input_request`` event means the run paused for HITL input — answer
        it with :meth:`resume`.
        """
        return self._stream_sse(
            f"/assistant/chat/{chat_id}/listen/{run_id}",
            organization_id=organization_id,
        )

    async def resume(
        self,
        chat_id: str,
        *,
        request_id: str,
        response: UserInputResponse | dict[str, Any],
        llm: ComposerLLMConfig | dict[str, Any],
        organization_id: str | None = None,
    ) -> AssistantResumeResponse:
        """Answer a paused HITL ``user_input_request`` and resume the run.

        ``llm`` is required (the executor rebuilds the chat model on resume).
        Returns a NEW ``run_id``; re-subscribe with :meth:`listen` on that run.
        """
        body: dict[str, Any] = {
            "request_id": request_id,
            "response": _to_payload(response),
            "llm": _to_payload(llm),
        }
        return AssistantResumeResponse.model_validate(
            await self._post(
                f"/assistant/chat/{chat_id}/resume",
                json=body,
                organization_id=organization_id,
            )
        )

    async def status(self, chat_id: str, *, organization_id: str | None = None) -> AssistantStatusResponse:
        """Return an assistant chat's status (running / awaiting_input / idle)."""
        return AssistantStatusResponse.model_validate(
            await self._get(f"/assistant/chat/{chat_id}/status", organization_id=organization_id)
        )

    async def cancel(self, chat_id: str, *, organization_id: str | None = None) -> AssistantCancelResponse:
        """Cancel a running assistant run (also clears any pending HITL question)."""
        return AssistantCancelResponse.model_validate(
            await self._post(f"/assistant/chat/{chat_id}/cancel", organization_id=organization_id)
        )

    async def delete(
        self,
        chat_id: str,
        *,
        permanent: bool = False,
        organization_id: str | None = None,
    ) -> AssistantDeleteResponse:
        """Delete an assistant chat (soft by default; ``permanent=True`` for hard delete)."""
        params: dict[str, Any] = {"permanent": permanent}
        return AssistantDeleteResponse.model_validate(
            await self._delete(
                f"/assistant/chat/{chat_id}",
                params=params,
                organization_id=organization_id,
            )
        )
