"""Shared/common type definitions."""

from __future__ import annotations

from typing_extensions import TypedDict


class PaginatedResponse(TypedDict, total=False):
    """Generic paginated response."""

    total: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool


class PagePaginatedResponse(TypedDict, total=False):
    """Page-based paginated response."""

    total: int
    page: int
    page_size: int
    total_pages: int


class SuccessResponse(TypedDict, total=False):
    """Generic success response."""

    success: bool
    message: str


class ErrorDetail(TypedDict, total=False):
    """Validation error detail."""

    loc: list[str]
    msg: str
    type: str
