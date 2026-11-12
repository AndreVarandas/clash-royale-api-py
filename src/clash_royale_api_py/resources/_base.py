"""Shared plumbing for resource classes.

Each resource exists in two flavors that read identically:

* ``Clans`` — methods return values directly.
* ``AsyncClans`` — same methods, ``await`` in front.

Both speak to a transport and never duplicate request-building logic.
"""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel

from .._responses import clean_params, parse_list, parse_page, parse_page_async
from .._transport import AsyncTransport, Transport
from ..pagination import AsyncPage, Page

ModelT = TypeVar("ModelT", bound=BaseModel)


class Resource:
    """Base for the synchronous resources."""

    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def _fetch(
        self, path: str, params: dict[str, Any] | None = None, model: type[ModelT] | None = None
    ) -> ModelT:
        assert model is not None, "internal error: model is required here"
        raw = self._transport.get_json(path, clean_params(params))
        return model.model_validate(raw)

    def _fetch_list(
        self, path: str, params: dict[str, Any] | None = None, model: type[ModelT] | None = None
    ) -> list[ModelT]:
        assert model is not None, "internal error: model is required here"
        raw = self._transport.get_json(path, clean_params(params))
        return parse_list(raw, model)

    def _fetch_page(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        model: type[ModelT] | None = None,
        items_key: str = "items",
    ) -> Page[ModelT]:
        assert model is not None, "internal error: model is required here"
        raw = self._transport.get_json(path, clean_params(params))

        def fetcher(after: str) -> Page[ModelT]:
            # Paging forward: a stale ``before`` cursor would contradict ``after``.
            next_params = {key: value for key, value in (params or {}).items() if key != "before"}
            next_params["after"] = after
            return self._fetch_page(path, next_params, model, items_key)

        return parse_page(raw, model, fetcher=fetcher, items_key=items_key)


class AsyncResource:
    """Base for the asynchronous resources."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def _fetch(
        self, path: str, params: dict[str, Any] | None = None, model: type[ModelT] | None = None
    ) -> ModelT:
        assert model is not None, "internal error: model is required here"
        raw = await self._transport.get_json(path, clean_params(params))
        return model.model_validate(raw)

    async def _fetch_list(
        self, path: str, params: dict[str, Any] | None = None, model: type[ModelT] | None = None
    ) -> list[ModelT]:
        assert model is not None, "internal error: model is required here"
        raw = await self._transport.get_json(path, clean_params(params))
        return parse_list(raw, model)

    async def _fetch_page(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        model: type[ModelT] | None = None,
        items_key: str = "items",
    ) -> AsyncPage[ModelT]:
        assert model is not None, "internal error: model is required here"
        raw = await self._transport.get_json(path, clean_params(params))

        async def fetcher(after: str) -> AsyncPage[ModelT]:
            # Paging forward: a stale ``before`` cursor would contradict ``after``.
            next_params = {key: value for key, value in (params or {}).items() if key != "before"}
            next_params["after"] = after
            return await self._fetch_page(path, next_params, model, items_key)

        return parse_page_async(raw, model, fetcher=fetcher, items_key=items_key)
