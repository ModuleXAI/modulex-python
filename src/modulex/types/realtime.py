"""Realtime / HITL wire-contract models (Pydantic v2).

Mirrors the backend ``app/models/composer_events.py`` discriminated unions used
by the composer & assistant human-in-the-loop (HITL) flow: when the agent pauses
via a LangGraph ``interrupt()`` it emits a ``user_input_request`` SSE event whose
``data`` is a :data:`UserInputRequest`; the client answers via ``resume()`` with a
:data:`UserInputResponse`.

These are shared by the composer and (later) assistant resources, so the HITL
contract lives in exactly one place.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, Optional, Union

from pydantic import Field, TypeAdapter

from modulex.types._models import ModulexModel

# ---------------------------------------------------------------------------
# LLM config (POST /composer/chat + /resume `llm`, POST /assistant/chat)
# ---------------------------------------------------------------------------


class ComposerLLMConfig(ModulexModel):
    """LLM provider config required by composer/assistant chat & resume.

    The backend rejects a bare string; it needs these structured fields.
    """

    integration_name: str
    provider_id: str
    model_id: str
    credential_id: Optional[str] = None


# ---------------------------------------------------------------------------
# UserInputRequest discriminated union (incoming HITL questions)
# ---------------------------------------------------------------------------


class UserInputRequestBase(ModulexModel):
    request_id: str
    message: str
    required: bool = True
    allow_free_text: bool = False
    context: Optional[dict[str, Any]] = None
    timeout_hint_seconds: Optional[int] = None


class ChoiceOption(ModulexModel):
    value: str
    label: str
    description: Optional[str] = None
    icon: Optional[str] = None
    badge: Optional[str] = None


class SingleChoiceRequest(UserInputRequestBase):
    kind: Literal["single_choice"] = "single_choice"
    options: list[ChoiceOption]


class MultiChoiceRequest(UserInputRequestBase):
    kind: Literal["multi_choice"] = "multi_choice"
    options: list[ChoiceOption]
    min_selections: int = 0
    max_selections: Optional[int] = None


class YesNoRequest(UserInputRequestBase):
    kind: Literal["yes_no"] = "yes_no"
    yes_label: str = "Yes"
    no_label: str = "No"


class FreeTextRequest(UserInputRequestBase):
    kind: Literal["free_text"] = "free_text"
    placeholder: Optional[str] = None
    multiline: bool = False
    min_length: int = 0
    max_length: Optional[int] = None


class CredentialAuthOption(ModulexModel):
    auth_type: Literal["oauth2", "api_key", "bearer_token", "modulex_key", "custom"]
    display_name: str
    fields: Optional[list[dict[str, Any]]] = None
    oauth_initiate_endpoint: Optional[str] = None
    setup_instructions: Optional[list[str]] = None
    test_supported: bool = False


class CredentialRequest(UserInputRequestBase):
    kind: Literal["credential_request"] = "credential_request"
    integration_name: str
    integration_display_name: str
    integration_logo: Optional[str] = None
    auth_options: list[CredentialAuthOption]
    pending_node_name: Optional[str] = None


UserInputRequest = Annotated[
    Union[
        SingleChoiceRequest,
        MultiChoiceRequest,
        YesNoRequest,
        FreeTextRequest,
        CredentialRequest,
    ],
    Field(discriminator="kind"),
]

_request_adapter: TypeAdapter[Any] = TypeAdapter(UserInputRequest)


def parse_user_input_request(payload: dict[str, Any]) -> Any:
    """Parse a raw HITL question dict into the correct UserInputRequest subtype."""
    return _request_adapter.validate_python(payload)


# ---------------------------------------------------------------------------
# UserInputResponse discriminated union (answers sent to resume())
# ---------------------------------------------------------------------------


class SingleChoiceResponse(ModulexModel):
    kind: Literal["single_choice"] = "single_choice"
    selected_value: Optional[str] = None
    free_text: Optional[str] = None


class MultiChoiceResponse(ModulexModel):
    kind: Literal["multi_choice"] = "multi_choice"
    selected_values: list[str]


class YesNoResponse(ModulexModel):
    kind: Literal["yes_no"] = "yes_no"
    answer: bool


class FreeTextResponse(ModulexModel):
    kind: Literal["free_text"] = "free_text"
    text: str


class CredentialAddedResponse(ModulexModel):
    kind: Literal["credential_added"] = "credential_added"
    credential_id: str
    integration_name: str
    auth_type: str


class CredentialFailedResponse(ModulexModel):
    kind: Literal["credential_failed"] = "credential_failed"
    integration_name: str
    auth_type: str
    error_code: Literal[
        "oauth_denied",
        "oauth_provider_error",
        "invalid_credentials",
        "network_error",
        "popup_closed",
        "timeout",
        "unknown",
    ]
    error_message: str
    retryable: bool = True
    provider_details: Optional[dict[str, Any]] = None


class SkippedResponse(ModulexModel):
    kind: Literal["skipped"] = "skipped"
    reason: Optional[str] = None


UserInputResponse = Annotated[
    Union[
        SingleChoiceResponse,
        MultiChoiceResponse,
        YesNoResponse,
        FreeTextResponse,
        CredentialAddedResponse,
        CredentialFailedResponse,
        SkippedResponse,
    ],
    Field(discriminator="kind"),
]

_response_adapter: TypeAdapter[Any] = TypeAdapter(UserInputResponse)


def parse_user_input_response(payload: dict[str, Any]) -> Any:
    """Parse a raw answer dict into the correct UserInputResponse subtype."""
    return _response_adapter.validate_python(payload)


# ---------------------------------------------------------------------------
# SSE event helpers & type inventories
# ---------------------------------------------------------------------------

#: Logical event types emitted on the workflow run stream (GET /workflows/listen).
#: NOTE: the backend's own Pydantic "design" models and its runtime emission
#: disagree on payload shape, so consume ``SSEEvent.data`` defensively.
WORKFLOW_EVENT_TYPES = frozenset(
    {
        "metadata",
        "node_started",
        "node_update",
        "node_error",
        "node_retry",
        "interrupt",
        "resumed",
        "done",
        "error",
        "cancelled",
        "heartbeat",
    }
)

#: Logical event types emitted on composer/assistant run streams.
COMPOSER_EVENT_TYPES = frozenset(
    {
        "metadata",
        "response_chunk",
        "tool_call",
        "tool_result",
        "workflow_change",
        "workflow_sync",
        "subagent_start",
        "user_input_request",
        "user_input_response",
        "interrupt",
        "interrupted",
        "run_resumed",
        "guidance",
        "pending",
        "applied",
        "pick",
        "text",
        "ai",
        "done",
        "error",
        "cancelled",
        "heartbeat",
    }
)


def user_input_request_from_event(data: dict[str, Any]) -> Any | None:
    """Extract a :data:`UserInputRequest` from a ``user_input_request`` event's data.

    Pass ``event.data`` from a composer/assistant listen stream; returns ``None``
    if the event is not a HITL question.
    """
    if not isinstance(data, dict) or data.get("type") != "user_input_request":
        return None
    payload = data.get("data")
    if not isinstance(payload, dict):
        return None
    return parse_user_input_request(payload)


def _to_payload(value: Any) -> Any:
    """Serialize a Pydantic model (or pass through a dict) for request bodies."""
    if isinstance(value, ModulexModel):
        return value.to_dict()
    return value
