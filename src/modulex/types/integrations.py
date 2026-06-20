"""Integration-related response models (Pydantic v2)."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class IntegrationAction(ModulexModel):
    """A single action exposed by a tool/knowledge integration."""

    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    parameters: dict[str, Any] = Field(default_factory=dict)


class IntegrationModel(ModulexModel):
    """A single model exposed by an LLM provider integration."""

    id: str
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    context_length: Optional[int] = None
    max_input_tokens: Optional[int] = None
    max_output_tokens: Optional[int] = None
    intelligence: Optional[Any] = None
    speed: Optional[Any] = None
    data_freshness: Optional[Any] = None
    supports_vision: Optional[bool] = None


class AuthSchema(ModulexModel):
    """An authentication schema for an integration.

    ``supports_modulex_oauth`` / ``supports_custom_oauth`` are only present on
    ``oauth2`` schemas returned by the detail endpoints (``tool_detail`` /
    ``llm_provider_detail`` / ``knowledge_provider_detail``); the generic
    ``get()`` endpoint does NOT enrich auth schemas with these fields.
    """

    auth_type: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    setup_environment_variables: list[Any] = Field(default_factory=list)
    setup_instructions: list[str] = Field(default_factory=list)
    oauth_config: Optional[Any] = None
    required_scopes: list[str] = Field(default_factory=list)
    important_notes: list[str] = Field(default_factory=list)
    supports_modulex_oauth: Optional[bool] = None
    supports_custom_oauth: Optional[bool] = None


class IntegrationMetadata(ModulexModel):
    """Metadata describing a single integration (browse/list item).

    ``actions`` / ``models`` / ``auth_schemas`` are only populated when
    ``include_details=True`` (browse); the plain list endpoints
    (``tools`` / ``llm_providers`` / ``knowledge_providers``) omit them.
    """

    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    app_url: Optional[str] = None
    docs_url: Optional[str] = None
    categories: list[str] = Field(default_factory=list)
    integration_type: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    recommended: bool = False
    actions: Optional[list[IntegrationAction]] = None
    models: Optional[list[IntegrationModel]] = None
    auth_schemas: Optional[list[AuthSchema]] = None


# Backward-compatible alias for the previous (drifted) name. Old field names
# (`type`, `category`, `auth_types`, `icon_url`) were fabricated and have been
# corrected to match the backend ``IntegrationMetadata`` shape.
IntegrationInfo = IntegrationMetadata


class IntegrationDetail(ModulexModel):
    """Full detail for a single integration (detail endpoints + generic get).

    Response shape varies by endpoint:
      - ``tool_detail`` / ``knowledge_provider_detail``: ``actions`` set, ``models`` absent.
      - ``llm_provider_detail``: ``models`` set, ``actions`` absent.
      - ``get``: both ``actions`` and ``models`` set; ``auth_schemas`` is NOT
        OAuth-enriched.
    """

    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    app_url: Optional[str] = None
    docs_url: Optional[str] = None
    categories: list[str] = Field(default_factory=list)
    integration_type: Optional[str] = None
    version: Optional[str] = None
    auth_schemas: list[AuthSchema] = Field(default_factory=list)
    actions: Optional[list[IntegrationAction]] = None
    models: Optional[list[IntegrationModel]] = None
    features: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


class IntegrationBrowseResponse(ModulexModel):
    """Paginated browse response from GET /integrations/browse."""

    integrations: list[IntegrationMetadata] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 50
    has_more: bool = False
