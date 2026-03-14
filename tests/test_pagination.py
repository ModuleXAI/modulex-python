"""Tests for pagination helpers."""

from __future__ import annotations

import httpx
import pytest
import respx

from modulex import Modulex


@pytest.mark.asyncio
class TestPagination:
    async def test_page_based_autopagination(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/workflows").mock(
            side_effect=[
                httpx.Response(
                    200,
                    json={
                        "workflows": [{"id": "1"}, {"id": "2"}],
                        "total": 5,
                        "page": 1,
                        "page_size": 2,
                        "total_pages": 3,
                    },
                ),
                httpx.Response(
                    200,
                    json={
                        "workflows": [{"id": "3"}, {"id": "4"}],
                        "total": 5,
                        "page": 2,
                        "page_size": 2,
                        "total_pages": 3,
                    },
                ),
                httpx.Response(
                    200,
                    json={
                        "workflows": [{"id": "5"}],
                        "total": 5,
                        "page": 3,
                        "page_size": 2,
                        "total_pages": 3,
                    },
                ),
            ]
        )
        items = []
        async for wf in client.workflows.list_all():
            items.append(wf)
        assert len(items) == 5
        assert [w["id"] for w in items] == ["1", "2", "3", "4", "5"]

    async def test_single_page(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/workflows").mock(
            return_value=httpx.Response(
                200,
                json={
                    "workflows": [{"id": "1"}],
                    "total": 1,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 1,
                },
            )
        )
        items = []
        async for wf in client.workflows.list_all():
            items.append(wf)
        assert len(items) == 1

    async def test_empty_result(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/workflows").mock(
            return_value=httpx.Response(
                200,
                json={
                    "workflows": [],
                    "total": 0,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 0,
                },
            )
        )
        items = []
        async for wf in client.workflows.list_all():
            items.append(wf)
        assert len(items) == 0
