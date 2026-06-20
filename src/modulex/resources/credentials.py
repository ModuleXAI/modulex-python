"""Credentials resource for the ModuleX Python SDK."""

from __future__ import annotations

import builtins
from typing import Any

from modulex._base import _BaseResource
from modulex._streaming import EventSourceStream
from modulex.types.credentials import (
    AuditEntry,
    CredentialDetailResponse,
    CredentialResponse,
    CredentialTestResult,
    CredentialUsageStats,
    MCPRefreshResponse,
    MCPServerCredentialResponse,
    MCPToolsResponse,
    OAuth2InitiateResponse,
    TestTemporaryCredentialResponse,
)


class Credentials(_BaseResource):
    """Resource for managing integration credentials."""

    async def list(
        self,
        *,
        integration_name: str | None = None,
        auth_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> Any:
        """Return a paginated list of credentials, optionally filtered by integration or auth type."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if integration_name is not None:
            params["integration_name"] = integration_name
        if auth_type is not None:
            params["auth_type"] = auth_type
        return await self._get("/credentials", params=params, organization_id=organization_id)

    async def get(
        self,
        credential_id: str,
        *,
        include_masked: bool = False,
        organization_id: str | None = None,
    ) -> CredentialDetailResponse:
        """Return a single credential by its ID, optionally including masked auth data."""
        return CredentialDetailResponse.model_validate(
            await self._get(
                f"/credentials/{credential_id}",
                params={"include_masked": include_masked},
                organization_id=organization_id,
            )
        )

    async def create(
        self,
        integration_name: str,
        *,
        auth_data: dict[str, Any] | None = None,
        auth_type: str | None = None,
        oauth_config: dict[str, Any] | None = None,
        display_name: str | None = None,
        metadata: dict[str, Any] | None = None,
        make_default: bool = False,
        expires_at: str | None = None,
        organization_id: str | None = None,
    ) -> CredentialResponse:
        """Create a new credential for the specified integration.

        The backend infers the credential type from ``auth_data``/``auth_type``:
        ``auth_data['api_key']`` -> API key; ``auth_data['token'|'bearer_token']``
        -> bearer; ``auth_data['access_token']`` + ``oauth_config`` -> OAuth2;
        ``auth_type='modulex_key'`` / ``'custom'``. For OAuth2 you must pass
        ``oauth_config`` (e.g. {client_id, client_secret, ...}). To register an MCP
        server, prefer :meth:`create_mcp_server`.
        """
        body: dict[str, Any] = {
            "integration_name": integration_name,
            "make_default": make_default,
        }
        if auth_data is not None:
            body["auth_data"] = auth_data
        if auth_type is not None:
            body["auth_type"] = auth_type
        if oauth_config is not None:
            body["oauth_config"] = oauth_config
        if display_name is not None:
            body["display_name"] = display_name
        if metadata is not None:
            body["metadata"] = metadata
        if expires_at is not None:
            body["expires_at"] = expires_at
        return CredentialResponse.model_validate(
            await self._post("/credentials", json=body, organization_id=organization_id)
        )

    async def initiate_oauth2(
        self,
        integration_name: str,
        *,
        redirect_uri: str,
        use_modulex_oauth: bool = True,
        custom_oauth_config: dict[str, Any] | None = None,
        scope: str | None = None,
        display_name: str | None = None,
        make_default: bool = False,
        env_var_values: dict[str, str] | None = None,
        composer_chat_id: str | None = None,
        composer_request_id: str | None = None,
        composer_llm_config: dict[str, Any] | None = None,
        organization_id: str | None = None,
    ) -> OAuth2InitiateResponse:
        """Begin an OAuth2 authorization flow; returns {authorization_url, state}.

        Open ``authorization_url`` in a browser; the provider redirects to the
        backend callback which creates the credential. Set ``use_modulex_oauth=False``
        and pass ``custom_oauth_config`` ({client_id, client_secret}) to use your own
        OAuth app. Requires admin/owner.
        """
        body: dict[str, Any] = {
            "integration_name": integration_name,
            "redirect_uri": redirect_uri,
            "use_modulex_oauth": use_modulex_oauth,
            "make_default": make_default,
        }
        if custom_oauth_config is not None:
            body["custom_oauth_config"] = custom_oauth_config
        if scope is not None:
            body["scope"] = scope
        if display_name is not None:
            body["display_name"] = display_name
        if env_var_values is not None:
            body["env_var_values"] = env_var_values
        if composer_chat_id is not None:
            body["composer_chat_id"] = composer_chat_id
        if composer_request_id is not None:
            body["composer_request_id"] = composer_request_id
        if composer_llm_config is not None:
            body["composer_llm_config"] = composer_llm_config
        return OAuth2InitiateResponse.model_validate(
            await self._post("/credentials/oauth2/initiate", json=body, organization_id=organization_id)
        )

    async def refresh_oauth2(self, credential_id: str, *, organization_id: str | None = None) -> CredentialResponse:
        """Refresh an OAuth2 credential's access token using its refresh token.

        Returns the updated (non-sensitive) credential. Requires admin/owner.
        """
        return CredentialResponse.model_validate(
            await self._post(
                f"/credentials/{credential_id}/oauth2/refresh",
                organization_id=organization_id,
            )
        )

    async def update(
        self,
        credential_id: str,
        *,
        display_name: str | None = None,
        metadata: dict[str, Any] | None = None,
        organization_id: str | None = None,
    ) -> CredentialResponse:
        """Update the display name or metadata of an existing credential."""
        body: dict[str, Any] = {}
        if display_name is not None:
            body["display_name"] = display_name
        if metadata is not None:
            body["metadata"] = metadata
        return CredentialResponse.model_validate(
            await self._put(
                f"/credentials/{credential_id}",
                json=body or None,
                organization_id=organization_id,
            )
        )

    async def delete(self, credential_id: str, *, organization_id: str | None = None) -> None:
        """Permanently delete a credential by its ID."""
        await self._delete(f"/credentials/{credential_id}", organization_id=organization_id)

    async def set_default(self, credential_id: str, *, organization_id: str | None = None) -> CredentialResponse:
        """Mark a credential as the default for its integration."""
        return CredentialResponse.model_validate(
            await self._post(
                f"/credentials/{credential_id}/set-default",
                organization_id=organization_id,
            )
        )

    async def test(self, credential_id: str, *, organization_id: str | None = None) -> CredentialTestResult:
        """Test an existing credential to verify it is still valid."""
        return CredentialTestResult.model_validate(
            await self._post(f"/credentials/{credential_id}/test", organization_id=organization_id)
        )

    async def test_temporary(
        self,
        integration_name: str,
        auth_type: str,
        auth_data: dict[str, Any],
        *,
        organization_id: str | None = None,
    ) -> TestTemporaryCredentialResponse:
        """Test a set of credentials without persisting them."""
        body: dict[str, Any] = {
            "integration_name": integration_name,
            "auth_type": auth_type,
            "auth_data": auth_data,
        }
        return TestTemporaryCredentialResponse.model_validate(
            await self._post("/credentials/test-temporary", json=body, organization_id=organization_id)
        )

    async def usage(
        self,
        credential_id: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        organization_id: str | None = None,
    ) -> CredentialUsageStats:
        """Return usage statistics for a credential within an optional date range."""
        params: dict[str, Any] = {}
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        return CredentialUsageStats.model_validate(
            await self._get(
                f"/credentials/{credential_id}/usage",
                params=params or None,
                organization_id=organization_id,
            )
        )

    async def audit(
        self,
        credential_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> builtins.list[AuditEntry]:
        """Return the audit log for a credential."""
        data = await self._get(
            f"/credentials/{credential_id}/audit",
            params={"limit": limit, "offset": offset},
            organization_id=organization_id,
        )
        return [AuditEntry.model_validate(item) for item in data]

    async def create_mcp_server(
        self,
        server_url: str,
        *,
        headers: dict[str, Any] | None = None,
        display_name: str | None = None,
        make_default: bool = False,
        organization_id: str | None = None,
    ) -> MCPServerCredentialResponse:
        """Register an MCP server as a credential."""
        body: dict[str, Any] = {"server_url": server_url, "make_default": make_default}
        if headers is not None:
            body["headers"] = headers
        if display_name is not None:
            body["display_name"] = display_name
        return MCPServerCredentialResponse.model_validate(
            await self._post("/credentials/mcp-server", json=body, organization_id=organization_id)
        )

    async def refresh_mcp_discovery(
        self, credential_id: str, *, organization_id: str | None = None
    ) -> MCPRefreshResponse:
        """Refresh the tool discovery for an MCP server credential."""
        return MCPRefreshResponse.model_validate(
            await self._post(
                f"/credentials/{credential_id}/refresh-discovery",
                organization_id=organization_id,
            )
        )

    async def mcp_tools(self, credential_id: str, *, organization_id: str | None = None) -> MCPToolsResponse:
        """Return the list of tools exposed by an MCP server credential."""
        return MCPToolsResponse.model_validate(
            await self._get(
                f"/credentials/{credential_id}/mcp-tools",
                organization_id=organization_id,
            )
        )

    def bulk_modulex_keys_stream(self, *, organization_id: str | None = None) -> EventSourceStream:
        """Open an SSE stream to receive bulk ModuleX key data."""
        return self._stream_sse(
            "/credentials/bulk-modulex-keys/stream",
            method="POST",
            organization_id=organization_id,
        )
