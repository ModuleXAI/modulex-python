"""Template-related type definitions."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class CreatorProfile(TypedDict, total=False):
    """Public creator profile attached to a template."""

    id: str
    user_id: str
    name: str
    about: str | None
    display_photo: str | None
    socials: dict[str, Any]
    created_at: str


class TemplateResponse(TypedDict, total=False):
    """Response representing a workflow template."""

    id: str
    creator_id: str
    creator: dict[str, Any]
    name: str
    description: str | None
    tags: list[str]
    workflow_schema: dict[str, Any]
    input: dict[str, Any]
    config: dict[str, Any]
    schema_image_url: str | None
    visibility: str
    status: str
    like_count: int
    used_count: int
    is_liked: bool
    edit_version: int
    created_at: str
    updated_at: str


class TemplateListResponse(TypedDict, total=False):
    """Paginated list response for templates."""

    templates: list[Any]
    total: int
    cached: bool
