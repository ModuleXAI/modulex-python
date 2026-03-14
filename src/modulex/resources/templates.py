"""Templates resource for the ModuleX Python SDK."""

from __future__ import annotations

import builtins
from typing import Any

from modulex._base import _BaseResource


class Templates(_BaseResource):
    """Resource for browsing, creating, and managing workflow templates."""

    async def list(self) -> Any:
        """Return all publicly available templates."""
        return await self._get("/templates")

    async def get(self, template_id: str) -> Any:
        """Return a single template by its ID."""
        return await self._get(f"/templates/{template_id}")

    async def my_templates(self) -> Any:
        """Return all templates created by the authenticated user."""
        return await self._get("/templates/me")

    async def create(
        self,
        workflow_id: str,
        name: str,
        *,
        description: str | None = None,
        tags: builtins.list[str] | None = None,
        schema_image_url: str | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Create a new template from an existing workflow."""
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "workflow_id": workflow_id,
                "name": name,
                "description": description,
                "tags": tags,
                "schema_image_url": schema_image_url,
            }.items()
            if v is not None
        }
        return await self._post("/templates", json=body, organization_id=organization_id)

    async def like(self, template_id: str) -> Any:
        """Toggle a like on a template for the authenticated user."""
        return await self._post(f"/templates/{template_id}/like")

    async def use(
        self,
        template_id: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Instantiate a workflow from a template into the caller's organization."""
        return await self._post(f"/templates/{template_id}/use", organization_id=organization_id)

    async def update_request(
        self,
        template_id: str,
        workflow_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        tags: builtins.list[str] | None = None,
        schema_image_url: str | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Submit an update request to refresh a published template from a workflow."""
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "workflow_id": workflow_id,
                "name": name,
                "description": description,
                "tags": tags,
                "schema_image_url": schema_image_url,
            }.items()
            if v is not None
        }
        return await self._post(
            f"/templates/{template_id}/update-request",
            json=body,
            organization_id=organization_id,
        )

    async def create_creator(
        self,
        name: str,
        *,
        about: str | None = None,
        display_photo: str | None = None,
        socials: dict[str, Any] | None = None,
    ) -> Any:
        """Create a creator profile for the authenticated user."""
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "about": about,
                "display_photo": display_photo,
                "socials": socials,
            }.items()
            if v is not None
        }
        return await self._post("/templates/creators", json=body)

    async def my_creator(self) -> Any:
        """Return the creator profile of the authenticated user."""
        return await self._get("/templates/creators/me")
