"""Credentials resource for the ModuleX Python SDK."""

from __future__ import annotations

from typing import Any

from modulex._base import _BaseResource
from modulex._streaming import EventSourceStream


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
    ) -> Any:
        """Return a single credential by its ID, optionally including masked auth data."""
        return await self._get(
            f"/credentials/{credential_id}",
            params={"include_masked": include_masked},
            organization_id=organization_id,
        )

    async def create(
        self,
        integration_name: str,
        *,
        auth_data: dict[str, Any] | None = None,
        auth_type: str | None = None,
        display_name: str | None = None,
        metadata: dict[str, Any] | None = None,
        make_default: bool = False,
        expires_at: str | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Create a new credential for the specified integration."""
        body: dict[str, Any] = {
            "integration_name": integration_name,
            "make_default": make_default,
        }
        if auth_data is not None:
            body["auth_data"] = auth_data
        if auth_type is not None:
            body["auth_type"] = auth_type
        if display_name is not None:
            body["display_name"] = display_name
        if metadata is not None:
            body["metadata"] = metadata
        if expires_at is not None:
            body["expires_at"] = expires_at
        return await self._post("/credentials", json=body, organization_id=organization_id)

    async def update(
        self,
        credential_id: str,
        *,
        display_name: str | None = None,
        metadata: dict[str, Any] | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Update the display name or metadata of an existing credential."""
        body: dict[str, Any] = {}
        if display_name is not None:
            body["display_name"] = display_name
        if metadata is not None:
            body["metadata"] = metadata
        return await self._put(
            f"/credentials/{credential_id}",
            json=body or None,
            organization_id=organization_id,
        )

    async def delete(self, credential_id: str, *, organization_id: str | None = None) -> None:
        """Permanently delete a credential by its ID."""
        await self._delete(f"/credentials/{credential_id}", organization_id=organization_id)

    async def set_default(self, credential_id: str, *, organization_id: str | None = None) -> Any:
        """Mark a credential as the default for its integration."""
        return await self._post(
            f"/credentials/{credential_id}/set-default",
            organization_id=organization_id,
        )

    async def test(self, credential_id: str, *, organization_id: str | None = None) -> Any:
        """Test an existing credential to verify it is still valid."""
        return await self._post(f"/credentials/{credential_id}/test", organization_id=organization_id)

    async def test_temporary(
        self,
        integration_name: str,
        auth_type: str,
        auth_data: dict[str, Any],
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Test a set of credentials without persisting them."""
        body: dict[str, Any] = {
            "integration_name": integration_name,
            "auth_type": auth_type,
            "auth_data": auth_data,
        }
        return await self._post("/credentials/test-temporary", json=body, organization_id=organization_id)

    async def usage(
        self,
        credential_id: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Return usage statistics for a credential within an optional date range."""
        params: dict[str, Any] = {}
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        return await self._get(
            f"/credentials/{credential_id}/usage",
            params=params or None,
            organization_id=organization_id,
        )

    async def audit(
        self,
        credential_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> Any:
        """Return the audit log for a credential."""
        return await self._get(
            f"/credentials/{credential_id}/audit",
            params={"limit": limit, "offset": offset},
            organization_id=organization_id,
        )

    async def create_mcp_server(
        self,
        server_url: str,
        *,
        headers: dict[str, Any] | None = None,
        display_name: str | None = None,
        make_default: bool = False,
        organization_id: str | None = None,
    ) -> Any:
        """Register an MCP server as a credential."""
        body: dict[str, Any] = {"server_url": server_url, "make_default": make_default}
        if headers is not None:
            body["headers"] = headers
        if display_name is not None:
            body["display_name"] = display_name
        return await self._post("/credentials/mcp-server", json=body, organization_id=organization_id)

    async def refresh_mcp_discovery(self, credential_id: str, *, organization_id: str | None = None) -> Any:
        """Refresh the tool discovery for an MCP server credential."""
        return await self._post(
            f"/credentials/{credential_id}/refresh-discovery",
            organization_id=organization_id,
        )

    async def mcp_tools(self, credential_id: str, *, organization_id: str | None = None) -> Any:
        """Return the list of tools exposed by an MCP server credential."""
        return await self._get(
            f"/credentials/{credential_id}/mcp-tools",
            organization_id=organization_id,
        )

    def bulk_modulex_keys_stream(self, *, organization_id: str | None = None) -> EventSourceStream:
        """Open an SSE stream to receive bulk ModuleX key data."""
        return self._stream_sse(
            "/credentials/bulk-modulex-keys/stream",
            method="POST",
            organization_id=organization_id,
        )
