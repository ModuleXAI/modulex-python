"""Dashboard-related response models (Pydantic v2).

Field shapes mirror the backend responses from ``app/api/dashboard.py``
(staging), not the UI types (which drift). See the dashboard drift report.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from modulex.types._models import ModulexModel

# --- Logs -------------------------------------------------------------------


class LogEntry(ModulexModel):
    """A single audit/activity log entry (item of data.logs[])."""

    id: str
    audit_time: Optional[str] = None  # ISO string
    category: Optional[str] = None
    operation: Optional[str] = None
    actor_email: Optional[str] = None
    message: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LogsData(ModulexModel):
    """The ``data`` block of the logs response (paginated logs)."""

    logs: list[LogEntry] = Field(default_factory=list)
    total_count: int = 0
    limit: int = 0
    offset: int = 0
    has_next: bool = False
    has_previous: bool = False


class LogsFilters(ModulexModel):
    """The ``filters`` block echoed back by the logs response."""

    category: Optional[str] = None
    operation: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ResponseMeta(ModulexModel):
    """The ``meta`` block shared across dashboard responses."""

    timestamp: Optional[str] = None
    period: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    cached: Optional[bool] = None


class LogsResponse(ModulexModel):
    """Response from GET /dashboard/logs."""

    success: bool = True
    organization_id: Optional[str] = None
    data: Optional[LogsData] = None
    filters: Optional[LogsFilters] = None
    meta: Optional[ResponseMeta] = None


# --- Analytics: overview ----------------------------------------------------


class CurrentMonthCreditUsage(ModulexModel):
    """Credit usage for the current billing month."""

    used_credit: float = 0.0
    max_credit: Optional[float] = None
    next_reset_date: Optional[str] = None


class SubscriptionPeriod(ModulexModel):
    """Current subscription billing period."""

    current_period_start: Optional[str] = None
    current_period_end: Optional[str] = None


class CredentialUsageLogEntry(ModulexModel):
    """A single credential-usage log row (overview.credential_usage_logs[])."""

    integration_name: Optional[str] = None
    service_name: Optional[str] = None
    auth_type: Optional[str] = None
    credential_display_name: Optional[str] = None
    success: Optional[bool] = None
    executed_at: Optional[str] = None
    user_email: Optional[str] = None


class OverviewData(ModulexModel):
    """The ``data.overview`` block of the analytics overview response."""

    active_member_count: int = 0
    configured_integrations_count: int = 0
    total_integrations_count: int = 0
    total_credentials_count: int = 0
    current_month_credit_usage: Optional[CurrentMonthCreditUsage] = None
    subscription: Optional[SubscriptionPeriod] = None
    credential_usage_logs: list[CredentialUsageLogEntry] = Field(default_factory=list)


class AnalyticsOverviewData(ModulexModel):
    """The ``data`` block of the analytics overview response."""

    overview: Optional[OverviewData] = None


class AnalyticsOverviewResponse(ModulexModel):
    """Response from GET /dashboard/analytics/overview."""

    success: bool = True
    organization_id: Optional[str] = None
    data: Optional[AnalyticsOverviewData] = None
    meta: Optional[ResponseMeta] = None


# --- Analytics: tools -------------------------------------------------------


class MostUsedAction(ModulexModel):
    """The most-used tool action (tools.most_used_action, nullable)."""

    action_name: Optional[str] = None
    integration_name: Optional[str] = None


class ToolUsageLog(ModulexModel):
    """A single tool-execution log row (tools.tool_usages[])."""

    user_email: Optional[str] = None
    integration_name: Optional[str] = None
    action_name: Optional[str] = None
    executed_at: Optional[str] = None
    execution_duration_ms: Optional[int] = None
    status: Optional[str] = None  # 'success' | 'error'
    credential_display_name: Optional[str] = None


class AnalyticsToolsData(ModulexModel):
    """The ``data`` block of the analytics tools response."""

    total_tool_executions: int = 0
    current_month_total_tool_executions: int = 0
    current_month_credit_usage: Optional[CurrentMonthCreditUsage] = None
    success_rate: float = 0.0
    most_used_action: Optional[MostUsedAction] = None
    configured_integrations_count: int = 0
    total_integrations_count: int = 0
    tool_usages: list[ToolUsageLog] = Field(default_factory=list)


class AnalyticsToolsResponse(ModulexModel):
    """Response from GET /dashboard/analytics/tools."""

    success: bool = True
    organization_id: Optional[str] = None
    data: Optional[AnalyticsToolsData] = None
    meta: Optional[ResponseMeta] = None


# --- Analytics: llm-usage ---------------------------------------------------


class LLMUsageLog(ModulexModel):
    """A single LLM-call log row (llm-usage.llm_usages[]).

    Backend column -> response key mappings: integration_name->provider,
    service_name->model, executed_at->request_time,
    execution_duration_ms->request_duration.
    """

    user_email: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    request_time: Optional[str] = None
    request_duration: Optional[int] = None
    status: Optional[str] = None  # 'success' | 'error'
    credential_display_name: Optional[str] = None


class AnalyticsLLMUsageData(ModulexModel):
    """The ``data`` block of the analytics llm-usage response."""

    total_llm_call: int = 0
    current_month_total_llm_call: int = 0
    current_month_credit_usage: Optional[CurrentMonthCreditUsage] = None
    request_success_rate: float = 0.0
    total_completion_tokens: int = 0
    total_prompt_tokens: int = 0
    llm_usages: list[LLMUsageLog] = Field(default_factory=list)


class AnalyticsLLMUsageResponse(ModulexModel):
    """Response from GET /dashboard/analytics/llm-usage."""

    success: bool = True
    organization_id: Optional[str] = None
    data: Optional[AnalyticsLLMUsageData] = None
    meta: Optional[ResponseMeta] = None


# --- Users ------------------------------------------------------------------


class DashboardUserEntry(ModulexModel):
    """A user row in the dashboard users list (member or invitation).

    Members and pending invitations share this shape; invitation-only fields
    (``is_invitation``, ``invitation_status``, ...) are absent for members.
    """

    id: str
    email: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_active_at: Optional[str] = None
    current_month_credit_usage: float = 0.0
    # Invitation-only fields
    is_invitation: bool = False
    invitation_status: Optional[str] = None
    invitation_expires_at: Optional[str] = None
    invited_user_id: Optional[str] = None
    invited_at: Optional[str] = None


class UserListResponse(ModulexModel):
    """Response from GET /dashboard/users."""

    success: bool = True
    organization_id: Optional[str] = None
    users: list[DashboardUserEntry] = Field(default_factory=list)
    invitation_count: int = 0
    max_seats: Optional[int] = None
    total: int = 0
    total_pages: int = 0
    current_page: int = 1
    limit: int = 0
    has_next: bool = False
    has_previous: bool = False
