"""Pydantic v2 base model + typed pagination for SDK responses.

All response models inherit from :class:`ModulexModel`. ``extra="allow"`` keeps
unknown fields the backend may add (accessible via the dict-compat shim), so the
SDK stays forward-compatible instead of dropping data it doesn't yet model.

The dict-compat shim (``__getitem__`` / ``get`` / ``__contains__``) lets callers
use either attribute access (``resp.status``, typed) or legacy dict access
(``resp["status"]``) during/after the migration from raw-dict returns.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ModulexModel(BaseModel):
    """Base class for all ModuleX SDK response models."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        ser_json_timedelta="iso8601",
    )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dict (aliases applied, None dropped)."""
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)

    # -- dict-compatibility shim -------------------------------------------------
    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            extra = self.model_extra or {}
            if key in extra:
                return extra[key]
            raise KeyError(key) from None

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-style accessor (declared fields first, then extra fields)."""
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        return key in type(self).model_fields or key in (self.model_extra or {})


class AsyncPage(Generic[T]):
    """Lazy async-iterable over a paginated endpoint, yielding typed items.

    Wraps an underlying dict paginator and validates each item into ``model``::

        async for wf in client.workflows.iter_all():  # -> AsyncPage[WorkflowResponse]
            print(wf.id)
    """

    def __init__(self, paginator: AsyncIterator[dict[str, Any]], model: Optional[type[T]] = None) -> None:
        self._paginator = paginator
        self._model = model

    def __aiter__(self) -> AsyncIterator[T]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[T]:
        async for item in self._paginator:
            if self._model is not None and isinstance(item, dict):
                yield self._model.model_validate(item)  # type: ignore[attr-defined]
            else:
                yield item  # type: ignore[misc]
