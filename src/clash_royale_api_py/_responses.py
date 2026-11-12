"""Turning raw JSON into models and pages, for both transports."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from pydantic import BaseModel

from .pagination import AsyncPage, Page, Paging

T = TypeVar("T", bound=BaseModel)

FetchSync = Callable[[str], "Page[Any]"]
FetchAsync = Callable[[str], Awaitable["AsyncPage[Any]"]]


def parse_list(raw: Any, model: type[T]) -> list[T]:
    """Parse a bare JSON array of objects into a list of models."""
    if isinstance(raw, dict):
        # Some endpoints occasionally wrap; be forgiving.
        raw = raw.get("items", [])
    return [model.model_validate(item) for item in raw or []]


def parse_page(
    raw: Any,
    model: type[T],
    fetcher: FetchSync | None = None,
    items_key: str = "items",
) -> Page[T]:
    """Parse a paginated response.

    The API usually answers ``{"items": [...], "paging": {...}}``; a few
    endpoints answer with a bare array. Both are handled.
    """
    items_raw = raw.get(items_key, []) if isinstance(raw, dict) else raw
    items = [model.model_validate(item) for item in items_raw or []]
    return Page(
        items=items,
        paging=Paging.from_raw(raw),
        raw=raw,
        fetcher=fetcher,
    )


def parse_page_async(
    raw: Any,
    model: type[T],
    fetcher: FetchAsync | None = None,
    items_key: str = "items",
) -> AsyncPage[T]:
    items_raw = raw.get(items_key, []) if isinstance(raw, dict) else raw
    items = [model.model_validate(item) for item in items_raw or []]
    return AsyncPage(
        items=items,
        paging=Paging.from_raw(raw),
        raw=raw,
        fetcher=fetcher,
    )


def clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Drop ``None`` values from query parameters."""
    if not params:
        return params
    cleaned = {key: value for key, value in params.items() if value is not None}
    return cleaned or None
