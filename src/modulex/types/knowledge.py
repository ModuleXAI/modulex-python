"""Knowledge base-related response models (Pydantic v2).

Aligned field-by-field with the backend ``app/api/knowledge.py`` response models
(NOT the UI types, which drift from the backend for several of these shapes).
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field
from typing_extensions import Literal

from modulex.types._models import ModulexModel

#: Knowledge base lifecycle status (CheckConstraint chk_kb_status).
KnowledgeBaseStatus = Literal["active", "processing", "error", "archived"]

#: Document processing status (CheckConstraint chk_doc_status).
DocumentStatus = Literal["pending", "processing", "completed", "failed"]

#: Supported document file types (CheckConstraint chk_doc_file_type).
FileType = Literal["pdf", "docx", "doc", "txt", "md", "html", "csv", "json", "xlsx", "pptx"]


class KnowledgeBaseResponse(ModulexModel):
    """A knowledge base (GET/POST /knowledge-bases)."""

    id: str
    organization_id: Optional[str] = None
    created_by_user_id: Optional[str] = None
    credential_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    embedding_config: dict[str, Any] = Field(default_factory=dict)
    chunking_config: dict[str, Any] = Field(default_factory=dict)
    document_count: int = 0
    total_chunks: int = 0
    total_tokens: int = 0
    status: Optional[KnowledgeBaseStatus] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    stats: Optional[dict[str, Any]] = None


class DocumentResponse(ModulexModel):
    """A document inside a knowledge base."""

    id: str
    knowledge_base_id: Optional[str] = None
    filename: Optional[str] = None
    file_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    status: Optional[DocumentStatus] = None
    chunk_count: int = 0
    token_count: int = 0
    error_message: Optional[str] = None
    created_at: Optional[str] = None


class DocumentStatusResponse(ModulexModel):
    """Processing status of a document (GET .../documents/{id}/status)."""

    document_id: Optional[str] = None
    status: Optional[DocumentStatus] = None
    filename: Optional[str] = None
    file_type: Optional[str] = None
    message: Optional[str] = None
    processing_started_at: Optional[str] = None
    processing_completed_at: Optional[str] = None
    chunk_count: Optional[int] = None
    token_count: Optional[int] = None
    error: Optional[str] = None


class SearchMatch(ModulexModel):
    """A single match from a knowledge base search."""

    chunk_id: str
    document_id: Optional[str] = None
    document_filename: Optional[str] = None
    chunk_index: Optional[int] = None
    score: Optional[float] = None
    content: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    # hybrid-search adds these:
    semantic_score: Optional[float] = None
    keyword_score: Optional[float] = None


class SearchResult(ModulexModel):
    """Result of a single-KB semantic search (POST .../{id}/search)."""

    query: Optional[str] = None
    knowledge_base_id: Optional[str] = None
    top_k: int = 0
    total_matches: int = 0
    matches: list[SearchMatch] = Field(default_factory=list)


class MultiSearchResult(ModulexModel):
    """Result of a multi-KB search (POST /knowledge-bases/search)."""

    query: Optional[str] = None
    knowledge_bases_searched: int = 0
    top_k: int = 0
    total_matches: int = 0
    matches: list[SearchMatch] = Field(default_factory=list)


class HybridSearchResult(ModulexModel):
    """Result of a hybrid (semantic + keyword) search (POST .../{id}/hybrid-search)."""

    query: Optional[str] = None
    knowledge_base_id: Optional[str] = None
    search_type: Optional[str] = None
    weights: dict[str, float] = Field(default_factory=dict)
    top_k: int = 0
    total_matches: int = 0
    matches: list[SearchMatch] = Field(default_factory=list)


class ChunkInfo(ModulexModel):
    """A single document chunk."""

    id: str
    document_id: Optional[str] = None
    chunk_index: Optional[int] = None
    content: Optional[str] = None
    content_preview: Optional[str] = None
    token_count: Optional[int] = None
    has_embedding: Optional[bool] = None
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    metadata: Optional[dict[str, Any]] = None
    created_at: Optional[str] = None


class DocumentChunksResponse(ModulexModel):
    """Response from GET .../documents/{id}/chunks."""

    chunks: list[ChunkInfo] = Field(default_factory=list)
    count: int = 0


class ContextResponse(ModulexModel):
    """Assembled RAG context (POST .../retrieve-context)."""

    context: Optional[str] = None
    query: Optional[str] = None


class SupportedFileTypesResponse(ModulexModel):
    """Supported file types and upload limits."""

    supported_types: list[str] = Field(default_factory=list)
    max_file_size_bytes: int = 0
    max_file_size_mb: float = 0.0


class KnowledgeStatsResponse(ModulexModel):
    """Aggregate org-level knowledge stats (GET /knowledge-bases/stats)."""

    knowledge_base_count: int = 0
    total_documents: int = 0
    total_chunks: int = 0
    total_tokens: int = 0
    total_file_size_bytes: int = 0
