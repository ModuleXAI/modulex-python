"""Tests for the Auth resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from modulex import Modulex


@pytest.mark.asyncio
class TestAuth:
    async def test_me(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/auth/me").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "user-123",
                    "email": "test@example.com",
                    "username": "testuser",
                    "role": "USER",
                    "is_active": True,
                },
            )
        )
        result = await client.auth.me()
        assert result["email"] == "test@example.com"
        assert result["role"] == "USER"

    async def test_organizations(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/auth/me/organizations").mock(
            return_value=httpx.Response(
                200,
                json={
                    "success": True,
                    "user_id": "user-123",
                    "organizations": [
                        {"id": "org-1", "name": "Test Org", "role": "owner"},
                    ],
                    "total": 1,
                },
            )
        )
        result = await client.auth.organizations()
        assert result["total"] == 1
        assert result["organizations"][0]["name"] == "Test Org"

    async def test_organizations_with_role_filter(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        route = mock_api.get("/auth/me/organizations").mock(
            return_value=httpx.Response(
                200,
                json={
                    "success": True,
                    "organizations": [],
                    "total": 0,
                },
            )
        )
        await client.auth.organizations(role="admin")
        assert route.calls.last.request.url.params.get("role") == "admin"

    async def test_invitations(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/auth/invitations/my").mock(
            return_value=httpx.Response(200, json={"invitations": [], "total": 0})
        )
        result = await client.auth.invitations()
        assert result["total"] == 0

    async def test_accept_invitation(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/auth/invitations/inv-123/accept").mock(return_value=httpx.Response(200, json={"success": True}))
        result = await client.auth.accept_invitation("inv-123")
        assert result["success"] is True

    async def test_reject_invitation(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/auth/invitations/inv-123/reject").mock(return_value=httpx.Response(200, json={"success": True}))
        result = await client.auth.reject_invitation("inv-123")
        assert result["success"] is True

    async def test_leave_organization(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/auth/organizations/leave").mock(
            return_value=httpx.Response(
                200,
                json={
                    "success": True,
                    "message": "Left organization",
                    "left_organization": {"id": "org-1", "name": "Old Org"},
                },
            )
        )
        result = await client.auth.leave_organization()
        assert result["success"] is True
