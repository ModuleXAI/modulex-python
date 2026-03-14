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

    def _build_headers(self, organization_id: str | None = None) -> dict[str, str]:
        """Build request headers with auth and optional org context."""
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self._client._config.api_key}",
            "Content-Type": "application/json",
        }
        org_id = self._resolve_org_id(organization_id)
        if org_id:
            headers["X-Organization-ID"] = org_id
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
        **kwargs: Any,
    ) -> Any:
        """Execute an HTTP request with retry logic."""
        url = f"{self._client._config.base_url}{path}"
        headers = self._build_headers(organization_id)

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
        **kwargs: Any,
    ) -> EventSourceStream:
        """Create an SSE stream connection."""
        url = f"{self._client._config.base_url}{path}"
        headers = self._build_headers(organization_id)
        headers.pop("Content-Type", None)
        return EventSourceStream(
            self._client._http,
            method,
            url,
            headers=headers,
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

    async def _paginate(
        self,
        path: str,
        *,
        items_key: str = "items",
        params: dict[str, Any] | None = None,
        organization_id: str | None = None,
        page_size: int = 20,
        **kwargs: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Auto-paginate through a list endpoint."""
        params = dict(params or {})

        # Detect pagination style
        if "page" in params or "page_size" in params:
            # Page-based pagination
            page = params.pop("page", 1)
            params["page_size"] = params.pop("page_size", page_size)
            while True:
                params["page"] = page
                result = await self._get(path, params=params, organization_id=organization_id, **kwargs)
                items = result.get(items_key, [])
                for item in items:
                    yield item
                total_pages = result.get("total_pages", 1)
                if page >= total_pages:
                    break
                page += 1
        else:
            # Limit/offset pagination
            offset = params.pop("offset", 0)
            limit = params.pop("limit", page_size)
            params["limit"] = limit
            while True:
                params["offset"] = offset
                result = await self._get(path, params=params, organization_id=organization_id, **kwargs)
                items = result.get(items_key, [])
                for item in items:
                    yield item
                if not result.get("has_next", False) or len(items) < limit:
                    break
                offset += limit
