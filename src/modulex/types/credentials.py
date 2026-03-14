"""Credential-related type definitions."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class CredentialResponse(TypedDict, total=False):
    """Response representing a stored credential."""

    credential_id: str
    integration_name: str
    integration_type: str
    display_name: str
    auth_type: str
    is_default: bool
    created_at: str
    updated_at: str
    last_used_at: str | None
    expires_at: str | None


class CredentialTestResult(TypedDict, total=False):
    """Result from testing a credential."""

    credential_id: str
    is_valid: bool
    message: str
    tested_at: str
    test_method: str
    integration_name: str
    auth_type: str
    test_endpoint: str | None
    status_code: int | None
    cost_level: str | None


class CredentialUsageStats(TypedDict, total=False):
    """Aggregated usage statistics for a credential."""

    credential_id: str
    total_calls: int
    successful_calls: int
    failed_calls: int
    success_rate: float
    action_breakdown: dict[str, Any]
    start_date: str
    end_date: str


class AuditEntry(TypedDict, total=False):
    """Single audit log entry for a credential action."""

    id: str
    credential_id: str
    action: str
    performed_by: str
    timestamp: str
    details: dict[str, Any]


class MCPToolsResponse(TypedDict, total=False):
    """Response listing MCP tools available for a credential."""

    credential_id: str
    tools: list[Any]
    total_count: int


class MCPRefreshResponse(TypedDict, total=False):
    """Response from refreshing MCP tools for a credential."""

    credential_id: str
    refreshed_at: str
    changes: dict[str, Any]
    total_tools: int
    success: bool
