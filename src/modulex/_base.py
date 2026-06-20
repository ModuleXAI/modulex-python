"""Base resource class with HTTP methods, retry logic, and error handling."""

from __future__ import annotations

import random
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

import httpx

from modulex._exceptions import (
    RETRYABLE_STATUS_CODES,
    TimeoutError,
    raise_for_status,
)
from modulex._streaming import EventSourceStream
from modulex._version import __version__

if TYPE_CHECKING:
    from modulex._client import Modulex


class _BaseResource:
    """Base class for all API resource classes."""

    def __init__(self, client: Modulex) -> None:
        self._client = client

    def _resolve_org_id(self, organization_id: str | None) -> str | None:
        """Resolve organization ID: per-request > client default > None."""
        if organization_id is not None:
            return organization_id
        return self._client._config.organization_id

    def _build_headers(
        self,
        organization_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, str]:
        """Build request headers with auth and optional org context.

        User-supplied ``default_headers`` may override the User-Agent but never
        the auth or content-type headers. ``idempotency_key`` (for mutating
        requests) is sent as the ``Idempotency-Key`` header so the backend can
        de-duplicate retried side-effectful operations.
        """
        headers: dict[str, str] = {
            "User-Agent": f"modulex-python/{__version__}",
            **self._client._config.default_headers,
            "Authorization": f"Bearer {self._client._config.api_key}",
            "Content-Type": "application/json",
        }
        org_id = self._resolve_org_id(organization_id)
        if org_id:
            headers["X-Organization-ID"] = org_id
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def _should_retry(self, method: str, status_code: int, attempt: int) -> bool:
        """Determine if a request should be retried."""
        if attempt >= self._client._config.max_retries:
            return False
        if status_code not in RETRYABLE_STATUS_CODES:
            return False
        if method.upper() not in ("GET", "HEAD"):
            return False
        return True

    @staticmethod
    def _backoff_delay(attempt: int, retry_after: float | None = None) -> float:
        """Calculate backoff delay with jitter."""
        if retry_after is not None:
            return retry_after
        base = 0.5
        delay: float = min(base * (2**attempt) + random.random() * 0.5, 30.0)
        return delay

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        organization_id: str | None = None,
        idempotency_key: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Execute an HTTP request with retry logic."""
        url = f"{self._client._config.base_url}{path}"
        headers = self._build_headers(organization_id, idempotency_key)

        # Filter None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        last_exc: Exception | None = None
        for attempt in range(self._client._config.max_retries + 1):
            try:
                response = await self._client._http.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=json,
                    timeout=self._client._config.timeout,
                    **kwargs,
                )
            except httpx.TimeoutException as e:
                if attempt < self._client._config.max_retries and method.upper() in ("GET", "HEAD"):
                    last_exc = e
                    import asyncio

                    await asyncio.sleep(self._backoff_delay(attempt))
                    continue
                raise TimeoutError(f"Request timed out: {e}") from e

            if response.status_code < 400:
                if response.status_code == 204:
                    return None
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    return response.json()
                try:
                    return response.json()
                except Exception:
                    return response.text

            if self._should_retry(method, response.status_code, attempt):
                retry_after: float | None = None
                if response.status_code == 429:
                    retry_after_header = response.headers.get("Retry-After")
                    if retry_after_header:
                        retry_after = float(retry_after_header)

                import asyncio

                await asyncio.sleep(self._backoff_delay(attempt, retry_after))
                continue

            raise_for_status(response)

        if last_exc:
            raise TimeoutError(f"Request timed out after {self._client._config.max_retries} retries") from last_exc
        raise_for_status(response)

    async def _get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        organization_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Execute a GET request."""
        return await self._request("GET", path, params=params, organization_id=organization_id, **kwargs)

    async def _post(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        organization_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Execute a POST request."""
        return await self._request("POST", path, json=json, organization_id=organization_id, **kwargs)

    async def _put(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        organization_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Execute a PUT request."""
        return await self._request("PUT", path, json=json, organization_id=organization_id, **kwargs)

    async def _patch(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        organization_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Execute a PATCH request."""
        return await self._request("PATCH", path, json=json, organization_id=organization_id, **kwargs)

    async def _delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        organization_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Execute a DELETE request."""
        return await self._request("DELETE", path, params=params, json=json, organization_id=organization_id, **kwargs)

    def _stream_sse(
        self,
        path: str,
        *,
        method: str = "GET",
        organization_id: str | None = None,
        json: dict[str, Any] | None = None,
        include_heartbeats: bool = False,
        **kwargs: Any,
    ) -> EventSourceStream:
        """Create an SSE stream connection.

        For POST streams (e.g. credentials bulk), pass ``json=`` — the JSON
        Content-Type is kept; for GET streams it is dropped.
        """
        url = f"{self._client._config.base_url}{path}"
        headers = self._build_headers(organization_id)
        if json is not None:
            kwargs["json"] = json
        else:
            headers.pop("Content-Type", None)
        return EventSourceStream(
            self._client._http,
            method,
            url,
            headers=headers,
            include_heartbeats=include_heartbeats,
            timeout=httpx.Timeout(self._client._config.timeout, read=None),
            **kwargs,
        )

    async def _upload(
        self,
        path: str,
        *,
        file: Any,
        filename: str,
        data: dict[str, str] | None = None,
        organization_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Execute a multipart file upload."""
        url = f"{self._client._config.base_url}{path}"
        headers = self._build_headers(organization_id)
        headers.pop("Content-Type", None)

        files = {"file": (filename, file)}

        response = await self._client._http.post(
            url,
            headers=headers,
            files=files,
            data=data,
            timeout=self._client._config.timeout,
            **kwargs,
        )

        if response.status_code >= 400:
            raise_for_status(response)

        return response.json()

    @staticmethod
    def _unwrap_page(result: Any, items_key: str) -> tuple[list[Any], dict[str, Any]]:
        """Return (items, container) handling a nested ``data.<items_key>`` envelope.

        e.g. dashboard/logs returns ``{success, data: {logs, total_count, has_next}}``.
        """
        if not isinstance(result, dict):
            return [], {}
        container = result
        if items_key not in result and isinstance(result.get("data"), dict):
            container = result["data"]
        items = container.get(items_key, [])
        return (items if isinstance(items, list) else []), container

    async def _paginate(
        self,
        path: str,
        *,
        items_key: str = "items",
        params: dict[str, Any] | None = None,
        organization_id: str | None = None,
        page_size: int = 20,
        style: str | None = None,
        total_key: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Auto-paginate a list endpoint across the backend's three styles.

        Styles (auto-detected from ``params`` unless ``style`` is given):
          - ``"page"``   — page / page_size, terminates on total_pages | has_more | short page
          - ``"offset"`` — limit / offset, terminates on has_next | has_more | total/total_count | short page
          - ``"cursor"`` — cursor / next_cursor (e.g. assistant & composer chat lists)
        """
        params = dict(params or {})

        if style is None:
            if "cursor" in params:
                style = "cursor"
            elif "page" in params or "page_size" in params:
                style = "page"
            else:
                style = "offset"

        if style == "cursor":
            cursor = params.pop("cursor", None)
            while True:
                if cursor is not None:
                    params["cursor"] = cursor
                result = await self._get(path, params=params, organization_id=organization_id, **kwargs)
                items, container = self._unwrap_page(result, items_key)
                for item in items:
                    yield item
                cursor = container.get("next_cursor")
                if not cursor or not items:
                    break

        elif style == "page":
            page = params.pop("page", 1)
            params["page_size"] = params.pop("page_size", page_size)
            while True:
                params["page"] = page
                result = await self._get(path, params=params, organization_id=organization_id, **kwargs)
                items, container = self._unwrap_page(result, items_key)
                for item in items:
                    yield item
                total_pages = container.get("total_pages")
                has_more = container.get("has_more")
                if total_pages is not None:
                    if page >= total_pages:
                        break
                elif has_more is not None:
                    if not has_more:
                        break
                elif len(items) < params["page_size"] or not items:
                    break
                page += 1

        else:  # offset
            offset = params.pop("offset", 0)
            limit = params.pop("limit", page_size)
            params["limit"] = limit
            while True:
                params["offset"] = offset
                result = await self._get(path, params=params, organization_id=organization_id, **kwargs)
                items, container = self._unwrap_page(result, items_key)
                for item in items:
                    yield item
                if not items:
                    break
                if container.get("has_next") is not None:
                    if not container["has_next"]:
                        break
                elif container.get("has_more") is not None:
                    if not container["has_more"]:
                        break
                else:
                    total = (
                        container.get(total_key)
                        if total_key
                        else (
                            container.get("total")
                            if container.get("total") is not None
                            else container.get("total_count")
                        )
                    )
                    if total is not None:
                        if offset + len(items) >= total:
                            break
                    elif len(items) < limit:
                        break
                offset += limit
