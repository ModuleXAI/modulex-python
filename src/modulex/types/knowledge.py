"""Knowledge base-related type definitions."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class KnowledgeBaseResponse(TypedDict, total=False):
    """Response representing a knowledge base."""

    id: str
    organization_id: str
    name: str
    description: str | None
    status: str
    embedding_config: dict[str, Any]
    chunking_config: dict[str, Any]
    document_count: int
    total_chunks: int
    created_at: str
    updated_at: str


class DocumentResponse(TypedDict, total=False):
    """Response representing a document inside a knowledge base."""

    id: str
    knowledge_base_id: str
    filename: str
    status: str
    file_size: int
    mime_type: str
    metadata: dict[str, Any]
    chunk_count: int
    created_at: str
    updated_at: str


class SearchResult(TypedDict, total=False):
    """Result from a knowledge base semantic search."""

    query: str
    results: list[dict[str, Any]]
    total_results: int


class ChunkInfo(TypedDict, total=False):
    """Information about a single document chunk."""

    id: str
    document_id: str
    content: str
    metadata: dict[str, Any]
    embedding_id: str | None


class ContextResponse(TypedDict, total=False):
    """Assembled context string returned for a query."""

    context: str
    query: str


class SupportedFileTypesResponse(TypedDict, total=False):
    """Supported file types and upload limits for a knowledge base."""

    supported_types: list[str]
    max_file_size_bytes: int
    max_file_size_mb: float


class KnowledgeStatsResponse(TypedDict, total=False):
    """Aggregate statistics for a knowledge base (shape may vary by backend)."""
