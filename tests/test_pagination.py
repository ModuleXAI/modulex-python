"""Tests for pagination helpers."""

from __future__ import annotations

import httpx
import pytest
import respx

from modulex import Modulex
from modulex._base import _BaseResource


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


@pytest.mark.asyncio
class TestPaginationStyles:
    """The three backend pagination styles via the generic _paginate helper."""

    async def test_cursor_pagination(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        mock_api.get("/composer/chats").mock(
            side_effect=[
                httpx.Response(200, json={"items": [{"id": "1"}, {"id": "2"}], "next_cursor": "2024-01-02T00:00:00Z"}),
                httpx.Response(200, json={"items": [{"id": "3"}], "next_cursor": None}),
            ]
        )
        res = _BaseResource(client)
        items = [i async for i in res._paginate("/composer/chats", items_key="items", params={"cursor": None})]
        assert [i["id"] for i in items] == ["1", "2", "3"]

    async def test_offset_has_more_pagination(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        # workflow-runs style: {runs, has_more, limit, offset} — NO total, flag is has_more.
        mock_api.get("/workflow-runs").mock(
            side_effect=[
                httpx.Response(
                    200, json={"runs": [{"id": "a"}, {"id": "b"}], "has_more": True, "limit": 2, "offset": 0}
                ),
                httpx.Response(200, json={"runs": [{"id": "c"}], "has_more": False, "limit": 2, "offset": 2}),
            ]
        )
        res = _BaseResource(client)
        items = [i async for i in res._paginate("/workflow-runs", items_key="runs", page_size=2)]
        assert [i["id"] for i in items] == ["a", "b", "c"]

    async def test_nested_envelope_pagination(self, client: Modulex, mock_api: respx.MockRouter) -> None:
        # dashboard/logs style: items live under data.logs, flag under data.has_next.
        mock_api.get("/dashboard/logs").mock(
            side_effect=[
                httpx.Response(
                    200,
                    json={"success": True, "data": {"logs": [{"id": "1"}], "has_next": True, "limit": 1, "offset": 0}},
                ),
                httpx.Response(
                    200,
                    json={"success": True, "data": {"logs": [{"id": "2"}], "has_next": False, "limit": 1, "offset": 1}},
                ),
            ]
        )
        res = _BaseResource(client)
        items = [i async for i in res._paginate("/dashboard/logs", items_key="logs", page_size=1)]
        assert [i["id"] for i in items] == ["1", "2"]
