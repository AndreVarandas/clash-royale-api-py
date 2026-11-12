"""Players: profiles, upcoming chests, and battle logs."""

from __future__ import annotations

from .._tags import tag_path_segment
from ..models import Battle, Player, UpcomingChests
from ._base import AsyncResource, Resource

__all__ = ["AsyncPlayers", "Players"]


class Players(Resource):
    """Everything about players."""

    def get(self, tag: str) -> Player:
        """Get a player by tag — ``"#2ABC"``, ``"2abc"``, all fine."""
        return self._fetch(f"/players/{tag_path_segment(tag)}", model=Player)

    def upcoming_chests(self, tag: str) -> UpcomingChests:
        """The reward chests the player will receive next, in order.

        The result is iterable: ``for chest in api.players.upcoming_chests(tag):``.
        """
        return self._fetch(f"/players/{tag_path_segment(tag)}/upcomingchests", model=UpcomingChests)

    def battle_log(self, tag: str) -> list[Battle]:
        """The player's recent battles, newest first."""
        return self._fetch_list(f"/players/{tag_path_segment(tag)}/battlelog", model=Battle)


class AsyncPlayers(AsyncResource):
    """Async counterpart of `Players`."""

    async def get(self, tag: str) -> Player:
        return await self._fetch(f"/players/{tag_path_segment(tag)}", model=Player)

    async def upcoming_chests(self, tag: str) -> UpcomingChests:
        return await self._fetch(
            f"/players/{tag_path_segment(tag)}/upcomingchests", model=UpcomingChests
        )

    async def battle_log(self, tag: str) -> list[Battle]:
        return await self._fetch_list(f"/players/{tag_path_segment(tag)}/battlelog", model=Battle)
