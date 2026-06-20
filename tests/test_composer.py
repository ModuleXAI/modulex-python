"""Tests for the Composer resource and the shared HITL/realtime models."""

from __future__ import annotations

import json as _json

import httpx
import pytest
import respx

from modulex import Modulex
from modulex.types.realtime import (
    ComposerLLMConfig,
    SingleChoiceRequest,
    YesNoResponse,
    parse_user_input_request,
    user_input_request_from_event,
)


@pytest.mark.asyncio
class TestComposer:
    async def test_chat_sends_llm_config_dict(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/composer/chat").mock(
            return_value=httpx.Response(200, json={"status": "running", "composer_chat_id": "c1", "run_id": "r1"})
        )
        await client.composer.chat(
            "build a workflow",
            llm=ComposerLLMConfig(integration_name="openai", provider_id="openai", model_id="gpt-4o-mini"),
        )
        sent = _json.loads(route.calls.last.request.content)
        assert sent["llm"] == {"integration_name": "openai", "provider_id": "openai", "model_id": "gpt-4o-mini"}
        assert sent["message"] == "build a workflow"

    async def test_chat_accepts_plain_llm_dict(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/composer/chat").mock(
            return_value=httpx.Response(200, json={"status": "running", "composer_chat_id": "c1"})
        )
        await client.composer.chat("hi", llm={"integration_name": "x", "provider_id": "y", "model_id": "z"})
        assert _json.loads(route.calls.last.request.content)["llm"]["model_id"] == "z"

    async def test_resume_body_shape(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/composer/chat/c1/resume").mock(
            return_value=httpx.Response(200, json={"status": "resuming", "run_id": "r2", "composer_chat_id": "c1"})
        )
        result = await client.composer.resume(
            "c1",
            request_id="q-1",
            response=YesNoResponse(answer=True),
            llm={"integration_name": "openai", "provider_id": "openai", "model_id": "gpt-4o-mini"},
        )
        sent = _json.loads(route.calls.last.request.content)
        assert sent["request_id"] == "q-1"
        assert sent["response"] == {"kind": "yes_no", "answer": True}
        assert sent["llm"]["model_id"] == "gpt-4o-mini"
        assert result["run_id"] == "r2"

    async def test_set_focus_always_sends_key_even_when_none(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.patch("/composer/chat/c1/focus").mock(
            return_value=httpx.Response(200, json={"composer_chat_id": "c1", "workflow_id": None})
        )
        await client.composer.set_focus("c1", None)  # unfocus
        sent = _json.loads(route.calls.last.request.content)
        assert "workflow_id" in sent  # key MUST be present
        assert sent["workflow_id"] is None

    async def test_list_cursor_params(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.get("/composer/chats").mock(
            return_value=httpx.Response(200, json={"items": [{"id": "c1"}], "next_cursor": None})
        )
        result = await client.composer.list(limit=10, cursor="2024-01-01T00:00:00Z")
        assert result["items"][0]["id"] == "c1"
        assert route.calls.last.request.url.params["cursor"] == "2024-01-01T00:00:00Z"
        assert route.calls.last.request.url.params["limit"] == "10"

    async def test_save_with_workflow_id(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.post("/composer/chat/c1/save").mock(
            return_value=httpx.Response(200, json={"status": "saved", "workflow_id": "wf-1"})
        )
        await client.composer.save("c1", workflow_id="wf-1")
        assert _json.loads(route.calls.last.request.content)["workflow_id"] == "wf-1"

    async def test_history_method_removed(self, client: Modulex) -> None:
        assert not hasattr(client.composer, "history")


class TestHITLModels:
    def test_parse_user_input_request_discriminates(self) -> None:
        payload = {
            "kind": "single_choice",
            "request_id": "q1",
            "message": "Pick one",
            "options": [{"value": "a", "label": "A"}, {"value": "b", "label": "B"}],
        }
        req = parse_user_input_request(payload)
        assert isinstance(req, SingleChoiceRequest)
        assert req.options[0].value == "a"

    def test_user_input_request_from_event(self) -> None:
        event_data = {
            "type": "user_input_request",
            "data": {"kind": "yes_no", "request_id": "q2", "message": "Proceed?"},
        }
        req = user_input_request_from_event(event_data)
        assert req is not None
        assert req.request_id == "q2"
        # non-HITL event returns None
        assert user_input_request_from_event({"type": "node_update"}) is None

    def test_response_serialization_drops_none(self) -> None:
        resp = YesNoResponse(answer=False)
        assert resp.to_dict() == {"kind": "yes_no", "answer": False}
