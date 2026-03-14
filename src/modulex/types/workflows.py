"""Workflow-related type definitions."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class LLMConfig(TypedDict, total=False):
    """LLM configuration."""

    integration_name: str
    provider_id: str
    model_id: str
    temperature: float
    credential_id: str | None


class ToolDefinition(TypedDict, total=False):
    """Tool definition for workflow nodes."""

    integration_name: str
    service_name: str
    credential_id: str | None
    parameter_defaults: dict[str, Any]
    parameter_overrides: dict[str, Any]


class RetryConfig(TypedDict, total=False):
    """Node retry configuration."""

    max_attempts: int
    initial_interval: float
    backoff_factor: float


class LLMNodeConfig(TypedDict, total=False):
    """LLM node configuration."""

    llm: LLMConfig
    system_prompt: str
    user_prompt: str
    structured_output_schema: dict[str, Any] | None


class ToolNodeConfig(TypedDict, total=False):
    """Tool node configuration."""

    tool: ToolDefinition
    input_mapping: dict[str, Any]


class AgentNodeConfig(TypedDict, total=False):
    """Agent node configuration."""

    llm: LLMConfig
    tools: list[ToolDefinition]
    system_prompt: str
    user_prompt: str
    max_iterations: int
    input_mapping: dict[str, Any]


class ExpressionBranch(TypedDict, total=False):
    """Conditional expression branch."""

    name: str
    condition: str
    target: str


class LoopConfig(TypedDict, total=False):
    """Loop configuration for conditional nodes."""

    loop_id: str
    mode: str
    iterations: int
    collection: str
    condition: str
    body_target: str
    body_end: str
    exit_target: str
    max_iterations: int


class ConditionalNodeConfig(TypedDict, total=False):
    """Conditional node configuration."""

    condition_type: str
    routes: dict[str, str]
    expression_branches: list[ExpressionBranch]
    loop_config: LoopConfig


class InterruptNodeConfig(TypedDict, total=False):
    """Interrupt node configuration."""

    message: str
    resume_schema: dict[str, Any]
    examples: list[Any]


class TransformerOperation(TypedDict, total=False):
    """Transformer operation."""

    type: str
    path: str
    condition: str
    template: str


class TransformerNodeConfig(TypedDict, total=False):
    """Transformer node configuration."""

    source: str
    operations: list[TransformerOperation]


class GuardrailsNodeConfig(TypedDict, total=False):
    """Guardrails node configuration."""

    rules: list[dict[str, Any]]
    on_violation: str


class KnowledgeNodeConfig(TypedDict, total=False):
    """Knowledge node configuration."""

    credential_id: str
    provider_type: str
    query: str
    collection_name: str
    top_k: int
    min_score: float
    filters: dict[str, Any]
    embedding_config: dict[str, Any]


class NodeDefinition(TypedDict, total=False):
    """Workflow node definition."""

    id: str
    type: str
    name: str
    description: str
    enabled: bool
    x: int
    y: int
    retry_config: RetryConfig
    llm_config: LLMNodeConfig
    tool_config: ToolNodeConfig
    agent_config: AgentNodeConfig
    function_config: dict[str, Any]
    conditional_config: ConditionalNodeConfig
    interrupt_config: InterruptNodeConfig
    transformer_config: TransformerNodeConfig
    guardrails_config: GuardrailsNodeConfig
    knowledge_config: KnowledgeNodeConfig


class EdgeDefinition(TypedDict):
    """Workflow edge definition."""

    source: str
    target: str


class StateField(TypedDict, total=False):
    """State schema field."""

    type: str
    description: str
    reducer: str
    required: bool
    default: Any


class StateSchema(TypedDict, total=False):
    """Workflow state schema."""

    fields: dict[str, StateField]


class WorkflowMetadata(TypedDict, total=False):
    """Workflow metadata."""

    name: str
    description: str
    version: str
    author: str
    tags: list[str]


class WorkflowConfig(TypedDict, total=False):
    """Workflow configuration."""

    default_llm: LLMConfig
    default_tools: list[ToolDefinition]
    recursion_limit: int
    checkpointing: str


class WorkflowDefinition(TypedDict, total=False):
    """Complete workflow definition schema."""

    metadata: WorkflowMetadata
    config: WorkflowConfig
    state_schema: StateSchema
    nodes: list[NodeDefinition]
    edges: list[EdgeDefinition]
    entry_point: str


class WorkflowResponse(TypedDict, total=False):
    """Workflow response from API."""

    id: str
    organization_id: str
    name: str
    description: str
    version: str
    tags: list[str]
    category: str
    status: str
    visibility: str
    workflow_schema: WorkflowDefinition
    input: dict[str, Any]
    config: dict[str, Any]
    edit_version: int
    last_edited_by: str | None
    last_edited_at: str | None
    created_at: str
    updated_at: str


class WorkflowListResponse(TypedDict, total=False):
    """Response from /workflows list."""

    workflows: list[WorkflowResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BuilderDetailsResponse(TypedDict, total=False):
    """Response from /workflows/builder/details."""

    node_types: dict[str, Any]
    categories: dict[str, Any]
    counts: dict[str, Any]
    cached: bool
