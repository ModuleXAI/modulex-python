"""Integration test configuration and fixtures.

Requires environment variables:
  MODULEX_API_KEY     — API key for authentication (required)
  MODULEX_ORG_ID      — Organization ID (required)
  MODULEX_BASE_URL    — API base URL (default: https://api.staging.modulex.dev)
  MODULEX_TEST_WORKFLOW_ID  — Existing workflow ID for execution tests (optional)
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio

from modulex import Modulex

# ---------------------------------------------------------------------------
# Load .env file automatically (if python-dotenv is installed)
# ---------------------------------------------------------------------------

try:
    from dotenv import load_dotenv

    # Walk up from this file to find the project root .env
    _env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass  # python-dotenv not installed — rely on shell environment

# ---------------------------------------------------------------------------
# Skip all integration tests when env vars are missing
# ---------------------------------------------------------------------------

MODULEX_API_KEY = os.environ.get("MODULEX_API_KEY", "")
MODULEX_ORG_ID = os.environ.get("MODULEX_ORG_ID", "")
MODULEX_BASE_URL = os.environ.get("MODULEX_BASE_URL", "https://api.staging.modulex.dev")
MODULEX_TEST_WORKFLOW_ID = os.environ.get("MODULEX_TEST_WORKFLOW_ID", "")

_MISSING_ENV = not MODULEX_API_KEY or not MODULEX_ORG_ID


@pytest.fixture(autouse=True)
def _require_env_vars() -> None:
    """Skip every integration test when required env vars are missing."""
    if _MISSING_ENV:
        pytest.skip("Integration tests require MODULEX_API_KEY and MODULEX_ORG_ID environment variables")


# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------


@dataclass
class CallResult:
    method: str
    path: str
    status: str  # "PASS", "FAIL", "SKIP"
    status_code: int | None = None
    duration_ms: float = 0.0
    detail: str = ""


@dataclass
class ResultTracker:
    results: list[CallResult] = field(default_factory=list)

    def record(
        self,
        method: str,
        path: str,
        *,
        status: str,
        status_code: int | None = None,
        duration_ms: float = 0.0,
        detail: str = "",
    ) -> None:
        result = CallResult(
            method=method,
            path=path,
            status=status,
            status_code=status_code,
            duration_ms=duration_ms,
            detail=detail,
        )
        self.results.append(result)
        icon = {"PASS": "\u2705", "FAIL": "\u274c", "SKIP": "\u23ed\ufe0f"}.get(status, "?")
        code_str = f" {status_code}" if status_code else ""
        detail_str = f": {detail}" if detail else ""
        print(f"  {icon} {status:<4}  {method:<6} {path} \u2014{code_str} ({duration_ms:.0f}ms){detail_str}")

    @property
    def passed(self) -> list[CallResult]:
        return [r for r in self.results if r.status == "PASS"]

    @property
    def failed(self) -> list[CallResult]:
        return [r for r in self.results if r.status == "FAIL"]

    @property
    def skipped(self) -> list[CallResult]:
        return [r for r in self.results if r.status == "SKIP"]


# Global tracker instance
_tracker = ResultTracker()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def api_key() -> str:
    return MODULEX_API_KEY


@pytest.fixture
def org_id() -> str:
    return MODULEX_ORG_ID


@pytest.fixture
def base_url() -> str:
    return MODULEX_BASE_URL


@pytest.fixture
def test_workflow_id() -> str:
    return MODULEX_TEST_WORKFLOW_ID


@pytest_asyncio.fixture
async def client(api_key: str, org_id: str, base_url: str) -> Modulex:
    if _MISSING_ENV:
        pytest.skip("Integration tests require MODULEX_API_KEY and MODULEX_ORG_ID")
    c = Modulex(
        api_key=api_key,
        organization_id=org_id,
        base_url=base_url,
        timeout=15.0,
    )
    yield c  # type: ignore[misc]
    await c.close()


@pytest.fixture(scope="session")
def tracker() -> ResultTracker:
    return _tracker


# ---------------------------------------------------------------------------
# Helper for timed API calls with automatic result tracking
# ---------------------------------------------------------------------------


class ApiCall:
    """Context manager that times an API call and records the result."""

    def __init__(self, tracker: ResultTracker, method: str, path: str) -> None:
        self._tracker = tracker
        self._method = method
        self._path = path
        self._start: float = 0
        self.result: Any = None

    async def __aenter__(self) -> ApiCall:
        self._start = time.monotonic()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        elapsed = (time.monotonic() - self._start) * 1000
        if exc_type is None:
            status_code = getattr(self.result, "status_code", 200) if self.result is not None else 200
            if isinstance(status_code, int):
                self._tracker.record(
                    self._method, self._path, status="PASS", status_code=status_code, duration_ms=elapsed
                )
            else:
                self._tracker.record(self._method, self._path, status="PASS", duration_ms=elapsed)
        else:
            detail = str(exc_val)[:120]
            status_code = getattr(exc_val, "status_code", None)
            self._tracker.record(
                self._method,
                self._path,
                status="FAIL",
                status_code=status_code,
                duration_ms=elapsed,
                detail=detail,
            )
        return False  # don't suppress exceptions


def api_call(tracker: ResultTracker, method: str, path: str) -> ApiCall:
    return ApiCall(tracker, method, path)


def skip_call(tracker: ResultTracker, method: str, path: str, reason: str) -> None:
    tracker.record(method, path, status="SKIP", detail=reason)


# ---------------------------------------------------------------------------
# Summary report at session end
# ---------------------------------------------------------------------------


def pytest_sessionfinish(session: Any, exitstatus: int) -> None:
    t = _tracker
    if not t.results:
        return

    total = len(t.results)
    passed = len(t.passed)
    failed = len(t.failed)
    skipped = len(t.skipped)

    print("\n")
    print("\u2550" * 54)
    print("  INTEGRATION TEST RESULTS")
    print("\u2550" * 54)
    print(f"  Total:    {total}")
    print(f"  Passed:   {passed}")
    print(f"  Failed:   {failed}")
    print(f"  Skipped:  {skipped}")

    if t.failed:
        print("\u2500" * 54)
        print("  FAILURES:")
        for r in t.failed:
            code = f" {r.status_code}" if r.status_code else ""
            print(f"  \u274c {r.method} {r.path} \u2014{code} {r.detail}")

    if t.skipped:
        print("\u2500" * 54)
        print("  SKIPPED:")
        for r in t.skipped:
            print(f"  \u23ed\ufe0f {r.method} {r.path} \u2014 {r.detail}")

    print("\u2550" * 54)
