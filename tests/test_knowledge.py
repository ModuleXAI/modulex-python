"""Tests for the Knowledge resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from modulex import Modulex


@pytest.mark.asyncio
class TestKnowledge:
    async def test_list(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/knowledge-bases").mock(return_value=httpx.Response(200, json={"items": [], "total": 0}))
        result = await client.knowledge.list()
        assert result["total"] == 0

    async def test_create(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/knowledge-bases").mock(
            return_value=httpx.Response(
                201,
                json={
                    "id": "kb-123",
                    "name": "Test KB",
                    "status": "active",
                },
            )
        )
        result = await client.knowledge.create(
            name="Test KB",
            embedding_config={"provider": "openai", "model": "text-embedding-3-small"},
        )
        assert result["id"] == "kb-123"

    async def test_get(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/knowledge-bases/kb-123").mock(
            return_value=httpx.Response(200, json={"id": "kb-123", "name": "Test KB"})
        )
        result = await client.knowledge.get("kb-123")
        assert result["id"] == "kb-123"

    async def test_delete(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.delete("/knowledge-bases/kb-123").mock(return_value=httpx.Response(204))
        result = await client.knowledge.delete("kb-123")
        assert result is None

    async def test_search(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/knowledge-bases/kb-123/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [{"content": "test", "score": 0.9}],
                    "total_results": 1,
                },
            )
        )
        result = await client.knowledge.search("kb-123", query="test query", top_k=5)
        assert result["total_results"] == 1

    async def test_multi_search(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/knowledge-bases/search").mock(
            return_value=httpx.Response(200, json={"results": [], "total_results": 0})
        )
        result = await client.knowledge.multi_search(
            knowledge_base_ids=["kb-1", "kb-2"],
            query="test",
        )
        assert result["total_results"] == 0

    async def test_hybrid_search(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/knowledge-bases/kb-123/hybrid-search").mock(
            return_value=httpx.Response(200, json={"results": [], "total_results": 0})
        )
        result = await client.knowledge.hybrid_search(
            "kb-123",
            query="test",
            keyword_weight=0.4,
            semantic_weight=0.6,
        )
        assert result["total_results"] == 0

    async def test_retrieve_context(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.post("/knowledge-bases/kb-123/retrieve-context").mock(
            return_value=httpx.Response(
                200,
                json={
                    "context": "Relevant context...",
                    "query": "test",
                },
            )
        )
        result = await client.knowledge.retrieve_context("kb-123", query="test")
        assert "context" in result

    async def test_supported_file_types(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/knowledge-bases/info/supported-file-types").mock(
            return_value=httpx.Response(
                200,
                json={
                    "supported_types": ["pdf", "docx", "txt"],
                    "max_file_size_mb": 50.0,
                },
            )
        )
        result = await client.knowledge.supported_file_types()
        assert "pdf" in result["supported_types"]

    async def test_list_documents(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/knowledge-bases/kb-123/documents").mock(
            return_value=httpx.Response(200, json={"items": [], "total": 0})
        )
        result = await client.knowledge.list_documents("kb-123")
        assert result["total"] == 0

    async def test_stats(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/knowledge-bases/stats").mock(
            return_value=httpx.Response(200, json={"total_bases": 5, "total_documents": 100})
        )
        result = await client.knowledge.stats()
        assert result["total_bases"] == 5
