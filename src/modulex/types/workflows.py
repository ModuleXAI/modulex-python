"""Workflow-related response models (Pydantic v2).

Field shapes follow the backend Pydantic models in ``app/models/workflow_schemas.py``
(the source of truth), not the UI types which drift. Per the migration leniency
rules, only entity primary ``id`` fields are required; everything else is optional
with a default so partial backend responses and simplified test mocks never raise
``ValidationError``.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class LLMConfig(ModulexModel):
    """LLM configuration."""

    integration_name: Optional[str] = None
    provider_id: Optional[str] = None
    model_id: Optional[str] = None
    temperature: Optional[float] = None
    credential_id: Optional[str] = None


class ToolDefinition(ModulexModel):
    """Tool definition for workflow nodes."""

    integration_name: Optional[str] = None
    service_name: Optional[str] = None
    credential_id: Optional[str] = None
    parameter_defaults: dict[str, Any] = Field(default_factory=dict)
    parameter_overrides: dict[str, Any] = Field(default_factory=dict)


class RetryConfig(ModulexModel):
    """Node retry configuration."""

    max_attempts: Optional[int] = None
    initial_interval: Optional[float] = None
    backoff_factor: Optional[float] = None


class LLMNodeConfig(ModulexModel):
    """LLM node configuration."""

    llm: Optional[LLMConfig] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    prompt_template: Optional[str] = None
    structured_output_schema: Optional[dict[str, Any]] = None
    structured_output_strict: bool = False


class ToolNodeConfig(ModulexModel):
    """Tool node configuration."""

    tool: Optional[ToolDefinition] = None
    input_mapping: dict[str, Any] = Field(default_factory=dict)


class AgentNodeConfig(ModulexModel):
    """Agent node configuration."""

    llm: Optional[LLMConfig] = None
    tools: list[ToolDefinition] = Field(default_factory=list)
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    prompt_template: Optional[str] = None
    max_iterations: Optional[int] = None
    input_mapping: dict[str, Any] = Field(default_factory=dict)


class FunctionNodeConfig(ModulexModel):
    """Function node configuration."""

    function_name: Optional[str] = None
    input_mapping: dict[str, Any] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)


class ExpressionBranch(ModulexModel):
    """Conditional expression branch (backend shape)."""

    id: Optional[str] = None
    source: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[Any] = None
    target: Optional[str] = None


class LoopConfig(ModulexModel):
    """Loop configuration for conditional nodes."""

    loop_id: Optional[str] = None
    mode: Optional[str] = None
    iterations: Optional[int] = None
    iterations_ref: Optional[str] = None
    collection: Optional[str] = None
    condition: Optional[str] = None
    body_target: Optional[str] = None
    body_end: Optional[str] = None
    exit_target: Optional[str] = None
    max_iterations: Optional[int] = None
    parallel: bool = False
    accumulate: bool = False
    accumulate_from: Optional[str] = None


class ConditionalNodeConfig(ModulexModel):
    """Conditional node configuration."""

    condition_type: Optional[str] = None
    routes: dict[str, str] = Field(default_factory=dict)
    expression: Optional[str] = None
    expression_branches: list[ExpressionBranch] = Field(default_factory=list)
    default_target: Optional[str] = None
    llm: Optional[LLMConfig] = None
    prompt_template: Optional[str] = None
    loop_config: Optional[LoopConfig] = None


class InterruptNodeConfig(ModulexModel):
    """Interrupt node configuration."""

    message: Optional[str] = None
    resume_schema: Optional[dict[str, Any]] = None
    examples: Optional[dict[str, Any]] = None


class TransformerOperation(ModulexModel):
    """Transformer operation (backend shape)."""

    type: Optional[str] = None
    field: Optional[str] = None
    params: dict[str, Any] = Field(default_factory=dict)


class TransformerNodeConfig(ModulexModel):
    """Transformer node configuration."""

    source: Optional[str] = None
    operations: list[TransformerOperation] = Field(default_factory=list)


class GuardrailsNodeConfig(ModulexModel):
    """Guardrails node configuration (backend shape)."""

    source: Optional[str] = None
    json_validation: Optional[dict[str, Any]] = None
    regex_validation: Optional[dict[str, Any]] = None
    hallucination_check: Optional[dict[str, Any]] = None
    pii_detection: Optional[dict[str, Any]] = None
    on_failure: Optional[str] = None
    failure_route: Optional[str] = None
    continue_on_partial_failure: bool = False


class KnowledgeNodeConfig(ModulexModel):
    """Knowledge node configuration."""

    credential_id: Optional[str] = None
    provider_type: Optional[str] = None
    query: Optional[str] = None
    query_from_input: Optional[str] = None
    collection_name: Optional[str] = None
    namespace: Optional[str] = None
    top_k: Optional[int] = None
    min_score: Optional[float] = None
    max_tokens: Optional[int] = None
    filters: dict[str, Any] = Field(default_factory=dict)
    document_ids: list[str] = Field(default_factory=list)
    output_format: Optional[str] = None
    include_metadata: bool = False
    include_source: bool = False
    embedding_config: dict[str, Any] = Field(default_factory=dict)


class NodeDefinition(ModulexModel):
    """Workflow node definition."""

    id: str
    type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True
    x: Optional[int] = None
    y: Optional[int] = None
    retry_config: Optional[RetryConfig] = None
    llm_config: Optional[LLMNodeConfig] = None
    tool_config: Optional[ToolNodeConfig] = None
    agent_config: Optional[AgentNodeConfig] = None
    function_config: Optional[FunctionNodeConfig] = None
    conditional_config: Optional[ConditionalNodeConfig] = None
    interrupt_config: Optional[InterruptNodeConfig] = None
    transformer_config: Optional[TransformerNodeConfig] = None
    guardrails_config: Optional[GuardrailsNodeConfig] = None
    knowledge_config: Optional[KnowledgeNodeConfig] = None


class ConditionDefinition(ModulexModel):
    """Edge condition definition for conditional routing."""

    type: Optional[str] = None
    expression: Optional[str] = None
    field: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[Any] = None


class EdgeDefinition(ModulexModel):
    """Workflow edge definition."""

    source: Optional[str] = None
    target: Optional[str] = None
    condition: Optional[ConditionDefinition] = None
    route_map: dict[str, Any] = Field(default_factory=dict)


class StateField(ModulexModel):
    """State schema field."""

    type: Optional[str] = None
    description: Optional[str] = None
    reducer: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None


class StateSchema(ModulexModel):
    """Workflow state schema."""

    fields: dict[str, StateField] = Field(default_factory=dict)


class WorkflowMetadata(ModulexModel):
    """Workflow metadata."""

    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class WorkflowConfig(ModulexModel):
    """Workflow configuration."""

    default_llm: Optional[LLMConfig] = None
    default_tools: list[ToolDefinition] = Field(default_factory=list)
    recursion_limit: int = 500
    enable_checkpointing: bool = False
    checkpointer_type: Optional[str] = None
    stream_mode: Optional[str] = None
    enable_subgraph_streaming: bool = False


class Position(ModulexModel):
    """Canvas position for the workflow start node."""

    x: Optional[float] = None
    y: Optional[float] = None


class WorkflowDefinition(ModulexModel):
    """Complete workflow definition schema."""

    metadata: Optional[WorkflowMetadata] = None
    config: Optional[WorkflowConfig] = None
    state_schema: Optional[StateSchema] = None
    nodes: list[NodeDefinition] = Field(default_factory=list)
    edges: list[EdgeDefinition] = Field(default_factory=list)
    entry_point: str = "__start__"
    start_position: Optional[Position] = None


class WorkflowResponse(ModulexModel):
    """Workflow record from POST/GET/PUT /workflows."""

    id: str
    organization_id: Optional[str] = None
    creator_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    category: Optional[str] = None
    status: Optional[str] = None
    visibility: Optional[str] = None
    workflow_schema: Optional[WorkflowDefinition] = None
    input: dict[str, Any] = Field(default_factory=dict)
    config: dict[str, Any] = Field(default_factory=dict)
    edit_version: Optional[int] = None
    last_edited_by: Optional[str] = None
    last_edited_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class WorkflowListResponse(ModulexModel):
    """Response from GET /workflows."""

    workflows: list[WorkflowResponse] = Field(default_factory=list)
    total: int = 0
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None


class BuilderCounts(ModulexModel):
    """``counts`` block of the builder details response."""

    integrations: int = 0
    functions: int = 0
    transformers: int = 0
    providers: int = 0


class BuilderCategories(ModulexModel):
    """``categories`` block of the builder details response."""

    tools: list[Any] = Field(default_factory=list)
    functions: list[Any] = Field(default_factory=list)
    transformers: list[Any] = Field(default_factory=list)


class BuilderDetailsResponse(ModulexModel):
    """Response from GET /workflows/builder/details."""

    node_types: dict[str, Any] = Field(default_factory=dict)
    categories: Optional[BuilderCategories] = None
    counts: Optional[BuilderCounts] = None
    features: dict[str, Any] = Field(default_factory=dict)
    cached: bool = False


class DeleteWorkflowResponse(ModulexModel):
    """Response from DELETE /workflows/{id}."""

    status: Optional[str] = None
    workflow_id: Optional[str] = None
    message: Optional[str] = None


class WorkflowChangeEvent(ModulexModel):
    """SSE payload from GET /workflows/{id}/changes.

    Tolerant union of ``connected | workflow_updated | user_joined | user_left``
    events. NOT returned by any method (``listen_changes`` returns an
    ``EventSourceStream``); defined for documentation and optional manual parsing.
    """

    type: Optional[str] = None
    workflow_id: Optional[str] = None
    edit_version: Optional[int] = None
    edited_by: Optional[str] = None
    source: Optional[str] = None
    timestamp: Optional[str] = None
