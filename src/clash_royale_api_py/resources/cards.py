"""Cards and current in-game events."""

from __future__ import annotations

import builtins

from ..models import Card, CardList, TrailEvent
from ..pagination import AsyncPage, Page
from ._base import AsyncResource, Resource

__all__ = ["AsyncCards", "AsyncEvents", "Cards", "Events"]


class Cards(Resource):
    """Every card in the game."""

    def list(
        self, *, limit: int | None = None, after: str | None = None, before: str | None = None
    ) -> Page[Card]:
        """List all available cards, as an iterable `Page`.

        Support items (tower troops etc.) live on the page's ``raw`` payload.
        """
        return self._fetch_page(
            "/cards",
            params={"limit": limit, "after": after, "before": before},
            model=Card,
            items_key="items",
        )

    def all(self) -> CardList:
        """Convenience: every card on one page, as a `CardList`."""
        return self._fetch("/cards", model=CardList)


class AsyncCards(AsyncResource):
    """Async counterpart of `Cards`."""

    async def list(
        self, *, limit: int | None = None, after: str | None = None, before: str | None = None
    ) -> AsyncPage[Card]:
        return await self._fetch_page(
            "/cards",
            params={"limit": limit, "after": after, "before": before},
            model=Card,
            items_key="items",
        )

    async def all(self) -> CardList:
        return await self._fetch("/cards", model=CardList)


class Events(Resource):
    """Current in-game events."""

    def list(self) -> builtins.list[TrailEvent]:
        """List ongoing events, with localized titles and descriptions."""
        return self._fetch_list("/events", model=TrailEvent)


class AsyncEvents(AsyncResource):
    """Async counterpart of `Events`."""

    async def list(self) -> builtins.list[TrailEvent]:
        return await self._fetch_list("/events", model=TrailEvent)
