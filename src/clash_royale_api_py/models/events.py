"""Leaderboard and event models."""

from __future__ import annotations

from typing import Any

from ._base import ClashRoyaleModel
from .common import JsonLocalizedName
from .players import PlayerClan

__all__ = ["Leaderboard", "LeaderboardEntry", "TrailEvent"]


class Leaderboard(ClashRoyaleModel):
    """A leaderboard available for the current trophy road season."""

    id: int | None = None
    name: str | JsonLocalizedName | None = None
    leagues: list[Any] | None = None

    def __repr__(self) -> str:
        return f"<Leaderboard id={self.id!r} {str(self.name or '')!r}>"


class LeaderboardEntry(ClashRoyaleModel):
    """A player on a trophy-road leaderboard."""

    tag: str | None = None
    name: str | None = None
    score: int | None = None
    rank: int | None = None
    updated: str | None = None
    clan: PlayerClan | None = None


class TrailEvent(ClashRoyaleModel):
    """An ongoing in-game event, with its localized title and description."""

    title: str | JsonLocalizedName | None = None
    description: str | JsonLocalizedName | None = None
    event_tag: str | None = None
