"""Credential-related response models (Pydantic v2)."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class CredentialResponse(ModulexModel):
    """A stored credential (non-sensitive view)."""

    credential_id: str
    integration_name: Optional[str] = None
    integration_type: Optional[str] = None
    display_name: Optional[str] = None
    auth_type: Optional[str] = None
    is_default: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_used_at: Optional[str] = None
    expires_at: Optional[str] = None
    credentials_metadata: Optional[dict[str, Any]] = None


class CredentialDetailResponse(CredentialResponse):
    """A stored credential with admin/detail fields (GET /credentials/{id})."""

    organization_id: Optional[str] = None
    created_by: Optional[str] = None
    created_by_email: Optional[str] = None
    auth_data_masked: Optional[str] = None


class MCPServerCredentialResponse(ModulexModel):
    """Response from POST /credentials/mcp-server."""

    credential_id: str
    integration_name: Optional[str] = None
    display_name: Optional[str] = None
    auth_type: Optional[str] = None
    is_default: bool = False
    created_at: Optional[str] = None
    credentials_metadata: Optional[dict[str, Any]] = None


class OAuth2InitiateResponse(ModulexModel):
    """Response from POST /credentials/oauth2/initiate."""

    authorization_url: Optional[str] = None
    state: Optional[str] = None


class CredentialTestResult(ModulexModel):
    """Result from testing an existing credential (POST /credentials/{id}/test)."""

    credential_id: Optional[str] = None
    is_valid: bool = False
    message: Optional[str] = None
    tested_at: Optional[str] = None


class TestTemporaryCredentialResponse(ModulexModel):
    """Result from testing a credential without persisting it (POST /credentials/test-temporary)."""

    is_valid: bool = False
    message: Optional[str] = None
    tested_at: Optional[str] = None
    test_method: Optional[str] = None
    integration_name: Optional[str] = None
    auth_type: Optional[str] = None
    test_endpoint: Optional[str] = None
    status_code: Optional[int] = None
    cost_level: Optional[str] = None


class CredentialUsageStats(ModulexModel):
    """Aggregated usage statistics for a credential (GET /credentials/{id}/usage)."""

    credential_id: Optional[str] = None
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    success_rate: float = 0.0
    action_breakdown: dict[str, int] = Field(default_factory=dict)
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class AuditEntry(ModulexModel):
    """A single audit log entry for a credential (GET /credentials/{id}/audit item)."""

    id: str
    credential_id: Optional[str] = None
    event_type: Optional[str] = None
    user_id: Optional[str] = None
    changes: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: Optional[str] = None


class MCPToolsResponse(ModulexModel):
    """Response listing MCP tools available for a credential (GET /credentials/{id}/mcp-tools)."""

    credential_id: Optional[str] = None
    tools: list[Any] = Field(default_factory=list)
    total_count: int = 0


class MCPRefreshResponse(ModulexModel):
    """Response from refreshing MCP tool discovery (POST /credentials/{id}/refresh-discovery)."""

    credential_id: Optional[str] = None
    refreshed_at: Optional[str] = None
    changes: Optional[dict[str, Any]] = None
    total_tools: int = 0
    success: bool = False
