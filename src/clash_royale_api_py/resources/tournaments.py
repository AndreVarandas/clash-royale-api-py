"""Tournaments: search by name, inspect one, and see the global ladder."""

from __future__ import annotations

import builtins

from .._tags import tag_path_segment
from ..models import LadderTournament, Tournament, TournamentHeader
from ..pagination import AsyncPage, Page
from ._base import AsyncResource, Resource

__all__ = ["AsyncGlobalTournaments", "AsyncTournaments", "GlobalTournaments", "Tournaments"]


class Tournaments(Resource):
    """Everything about tournaments."""

    def search(
        self,
        *,
        name: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[TournamentHeader]:
        """Search tournaments by name (at least three characters)."""
        return self._fetch_page(
            "/tournaments",
            params={"name": name, "limit": limit, "after": after, "before": before},
            model=TournamentHeader,
        )

    def get(self, tag: str) -> Tournament:
        """Get one tournament by its tag."""
        return self._fetch(f"/tournaments/{tag_path_segment(tag)}", model=Tournament)


class AsyncTournaments(AsyncResource):
    """Async counterpart of `Tournaments`."""

    async def search(
        self,
        *,
        name: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[TournamentHeader]:
        return await self._fetch_page(
            "/tournaments",
            params={"name": name, "limit": limit, "after": after, "before": before},
            model=TournamentHeader,
        )

    async def get(self, tag: str) -> Tournament:
        return await self._fetch(f"/tournaments/{tag_path_segment(tag)}", model=Tournament)


class GlobalTournaments(Resource):
    """The global tournaments anyone can join right now."""

    def list(self) -> builtins.list[LadderTournament]:
        """List all available global tournaments."""
        return self._fetch_list("/globaltournaments", model=LadderTournament)


class AsyncGlobalTournaments(AsyncResource):
    """Async counterpart of `GlobalTournaments`."""

    async def list(self) -> builtins.list[LadderTournament]:
        return await self._fetch_list("/globaltournaments", model=LadderTournament)
