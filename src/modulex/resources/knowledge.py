"""Knowledge resource for the ModuleX Python SDK."""

from __future__ import annotations

import builtins
import json as json_module
import os
from typing import Any

from modulex._base import _BaseResource


class Knowledge(_BaseResource):
    """Resource for managing knowledge bases, documents, and semantic search."""

    async def list(
        self,
        *,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> Any:
        """Return all knowledge bases accessible to the caller."""
        params: dict[str, Any] = {
            k: v for k, v in {"status": status, "limit": limit, "offset": offset}.items() if v is not None
        }
        return await self._get("/knowledge-bases", params=params, organization_id=organization_id)

    async def create(
        self,
        name: str,
        *,
        description: str | None = None,
        embedding_config: dict[str, Any] | None = None,
        chunking_config: dict[str, Any] | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Create a new knowledge base with the given name and optional configuration."""
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "description": description,
                "embedding_config": embedding_config,
                "chunking_config": chunking_config,
            }.items()
            if v is not None
        }
        return await self._post("/knowledge-bases", json=body, organization_id=organization_id)

    async def get(
        self,
        knowledge_base_id: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Return a single knowledge base by its ID."""
        return await self._get(f"/knowledge-bases/{knowledge_base_id}", organization_id=organization_id)

    async def update(
        self,
        knowledge_base_id: str,
        *,
        organization_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Update an existing knowledge base with the provided field values."""
        body: dict[str, Any] = {k: v for k, v in kwargs.items() if v is not None}
        return await self._put(
            f"/knowledge-bases/{knowledge_base_id}",
            json=body,
            organization_id=organization_id,
        )

    async def delete(
        self,
        knowledge_base_id: str,
        *,
        delete_files: bool = True,
        organization_id: str | None = None,
    ) -> None:
        """Delete a knowledge base and optionally its associated files."""
        params: dict[str, Any] = {"delete_files": delete_files}
        await self._delete(
            f"/knowledge-bases/{knowledge_base_id}",
            params=params,
            organization_id=organization_id,
        )

    async def archive(
        self,
        knowledge_base_id: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Archive a knowledge base, making it read-only."""
        return await self._post(
            f"/knowledge-bases/{knowledge_base_id}/archive",
            organization_id=organization_id,
        )

    async def stats(self, *, organization_id: str | None = None) -> Any:
        """Return aggregate statistics for all knowledge bases in the organization."""
        return await self._get("/knowledge-bases/stats", organization_id=organization_id)

    async def list_documents(
        self,
        knowledge_base_id: str,
        *,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> Any:
        """Return all documents within a knowledge base."""
        params: dict[str, Any] = {
            k: v for k, v in {"status": status, "limit": limit, "offset": offset}.items() if v is not None
        }
        return await self._get(
            f"/knowledge-bases/{knowledge_base_id}/documents",
            params=params,
            organization_id=organization_id,
        )

    async def upload_document(
        self,
        knowledge_base_id: str,
        *,
        file_path: str | None = None,
        file: Any | None = None,
        filename: str | None = None,
        metadata: dict[str, Any] | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Upload a document to a knowledge base via multipart form data."""
        if file_path is not None:
            f = open(file_path, "rb")
            fn = filename or os.path.basename(file_path)
        elif file is not None:
            f = file
            fn = filename or "document"
        else:
            raise ValueError("Either file_path or file must be provided")

        data: dict[str, str] = {}
        if metadata is not None:
            data["metadata"] = json_module.dumps(metadata)

        try:
            return await self._upload(
                f"/knowledge-bases/{knowledge_base_id}/documents",
                file=f,
                filename=fn,
                data=data if data else None,
                organization_id=organization_id,
            )
        finally:
            if file_path is not None:
                f.close()

    async def get_document(
        self,
        knowledge_base_id: str,
        document_id: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Return a single document within a knowledge base by its ID."""
        return await self._get(
            f"/knowledge-bases/{knowledge_base_id}/documents/{document_id}",
            organization_id=organization_id,
        )

    async def document_status(
        self,
        knowledge_base_id: str,
        document_id: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Return the processing status of a document."""
        return await self._get(
            f"/knowledge-bases/{knowledge_base_id}/documents/{document_id}/status",
            organization_id=organization_id,
        )

    async def delete_document(
        self,
        knowledge_base_id: str,
        document_id: str,
        *,
        delete_file: bool = True,
        organization_id: str | None = None,
    ) -> None:
        """Delete a document from a knowledge base and optionally its underlying file."""
        params: dict[str, Any] = {"delete_file": delete_file}
        await self._delete(
            f"/knowledge-bases/{knowledge_base_id}/documents/{document_id}",
            params=params,
            organization_id=organization_id,
        )

    async def retry_document(
        self,
        knowledge_base_id: str,
        document_id: str,
        *,
        organization_id: str | None = None,
    ) -> Any:
        """Retry processing for a failed document."""
        return await self._post(
            f"/knowledge-bases/{knowledge_base_id}/documents/{document_id}/retry",
            organization_id=organization_id,
        )

    async def document_chunks(
        self,
        knowledge_base_id: str,
        document_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> Any:
        """Return the text chunks produced from a document after processing."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        return await self._get(
            f"/knowledge-bases/{knowledge_base_id}/documents/{document_id}/chunks",
            params=params,
            organization_id=organization_id,
        )

    async def search(
        self,
        knowledge_base_id: str,
        query: str,
        *,
        top_k: int = 5,
        min_score: float = 0.0,
        filters: dict[str, Any] | None = None,
        include_content: bool = True,
        include_metadata: bool = True,
        organization_id: str | None = None,
    ) -> Any:
        """Perform a semantic vector search against a knowledge base."""
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "query": query,
                "top_k": top_k,
                "min_score": min_score,
                "filters": filters,
                "include_content": include_content,
                "include_metadata": include_metadata,
            }.items()
            if v is not None
        }
        return await self._post(
            f"/knowledge-bases/{knowledge_base_id}/search",
            json=body,
            organization_id=organization_id,
        )

    async def multi_search(
        self,
        knowledge_base_ids: builtins.list[str],
        query: str,
        *,
        top_k: int = 5,
        min_score: float = 0.0,
        organization_id: str | None = None,
    ) -> Any:
        """Search across multiple knowledge bases in a single request."""
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "knowledge_base_ids": knowledge_base_ids,
                "query": query,
                "top_k": top_k,
                "min_score": min_score,
            }.items()
            if v is not None
        }
        return await self._post("/knowledge-bases/search", json=body, organization_id=organization_id)

    async def hybrid_search(
        self,
        knowledge_base_id: str,
        query: str,
        *,
        top_k: int = 5,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7,
        min_score: float = 0.0,
        filters: dict[str, Any] | None = None,
        organization_id: str | None = None,
    ) -> Any:
        """Perform a hybrid keyword-plus-semantic search against a knowledge base."""
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "query": query,
                "top_k": top_k,
                "keyword_weight": keyword_weight,
                "semantic_weight": semantic_weight,
                "min_score": min_score,
                "filters": filters,
            }.items()
            if v is not None
        }
        return await self._post(
            f"/knowledge-bases/{knowledge_base_id}/hybrid-search",
            json=body,
            organization_id=organization_id,
        )

    async def retrieve_context(
        self,
        knowledge_base_id: str,
        query: str,
        *,
        max_tokens: int = 2000,
        top_k: int = 10,
        min_score: float = 0.3,
        organization_id: str | None = None,
    ) -> Any:
        """Retrieve a token-bounded context string suitable for LLM prompts."""
        body: dict[str, Any] = {
            "query": query,
            "max_tokens": max_tokens,
            "top_k": top_k,
            "min_score": min_score,
        }
        return await self._post(
            f"/knowledge-bases/{knowledge_base_id}/retrieve-context",
            json=body,
            organization_id=organization_id,
        )

    async def supported_file_types(self) -> Any:
        """Return the list of file types supported for document upload."""
        return await self._get("/knowledge-bases/info/supported-file-types")
