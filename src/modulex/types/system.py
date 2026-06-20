"""System / health response models (Pydantic v2)."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from modulex.types._models import ModulexModel


class SystemHealthResponse(ModulexModel):
    """Response from GET /system/health (public, simple status)."""

    status: Optional[str] = None
    service: Optional[str] = None
    version: Optional[str] = None


class TimezoneOption(ModulexModel):
    """A single selectable timezone (item of search/group results)."""

    value: Optional[str] = None
    label: Optional[str] = None
    offset: Optional[str] = None


class TimezoneGroup(ModulexModel):
    """A region-grouped set of timezones inside ``popular``."""

    region: Optional[str] = None
    timezones: list[TimezoneOption] = Field(default_factory=list)


class TimezoneListResponse(ModulexModel):
    """Response from GET /system/timezones.

    Note: ``popular`` is a ``list[TimezoneGroup]`` (backend wire shape), not a
    region-keyed dict (the UI type drifted and models it incorrectly).
    """

    popular: list[TimezoneGroup] = Field(default_factory=list)
    all_timezones: list[str] = Field(default_factory=list)


class CheckResult(ModulexModel):
    """A single diagnostic check inside an OAuth HealthReport."""

    name: Optional[str] = None
    status: Optional[str] = None
    summary: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    suggestion: Optional[str] = None


class HealthReport(ModulexModel):
    """Response from GET /system/health/oauth (API-key gated diagnostics)."""

    schema_version: int = 1
    overall: Optional[str] = None
    generated_at: Optional[str] = None
    checks: list[CheckResult] = Field(default_factory=list)
