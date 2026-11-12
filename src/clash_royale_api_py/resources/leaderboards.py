"""Trophy-road leaderboards."""

from __future__ import annotations

import builtins

from ..models import Leaderboard, LeaderboardEntry
from ..pagination import AsyncPage, Page
from ._base import AsyncResource, Resource

__all__ = ["AsyncLeaderboards", "Leaderboards"]


class Leaderboards(Resource):
    """Trophy-road leaderboards."""

    def list(self) -> builtins.list[Leaderboard]:
        """List all leaderboards; competitive ones expose their leagues too."""
        return self._fetch_list("/leaderboards", model=Leaderboard)

    def get(
        self,
        leaderboard_id: int,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[LeaderboardEntry]:
        """The players on one leaderboard."""
        return self._fetch_page(
            f"/leaderboard/{leaderboard_id}",
            params={"limit": limit, "after": after, "before": before},
            model=LeaderboardEntry,
        )

    def league(
        self,
        leaderboard_id: int,
        league_id: int,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[LeaderboardEntry]:
        """The players on one competitive league of a leaderboard."""
        return self._fetch_page(
            f"/leaderboard/{leaderboard_id}/leagues/{league_id}",
            params={"limit": limit, "after": after, "before": before},
            model=LeaderboardEntry,
        )


class AsyncLeaderboards(AsyncResource):
    """Async counterpart of `Leaderboards`."""

    async def list(self) -> builtins.list[Leaderboard]:
        return await self._fetch_list("/leaderboards", model=Leaderboard)

    async def get(
        self,
        leaderboard_id: int,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[LeaderboardEntry]:
        return await self._fetch_page(
            f"/leaderboard/{leaderboard_id}",
            params={"limit": limit, "after": after, "before": before},
            model=LeaderboardEntry,
        )

    async def league(
        self,
        leaderboard_id: int,
        league_id: int,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[LeaderboardEntry]:
        return await self._fetch_page(
            f"/leaderboard/{leaderboard_id}/leagues/{league_id}",
            params={"limit": limit, "after": after, "before": before},
            model=LeaderboardEntry,
        )
