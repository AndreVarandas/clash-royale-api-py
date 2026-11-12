"""The polite escape hatch: talk to any endpoint directly."""

from __future__ import annotations

from typing import Any

from ._base import AsyncResource, Resource

__all__ = ["AsyncRaw", "Raw"]


class Raw(Resource):
    """Call any endpoint the library doesn't wrap yet.

    Example::

        data = api.raw.get("/players/%232PP/verifytoken")
    """

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET *path* (relative to the base URL) and return parsed JSON."""
        return self._transport.get_json(path, params)


class AsyncRaw(AsyncResource):
    """Async counterpart of `Raw`."""

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self._transport.get_json(path, params)
