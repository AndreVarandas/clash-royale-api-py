"""Ranking models for locations and seasons."""

from __future__ import annotations

from ._base import ClashRoyaleModel
from .common import Arena, BadgeUrls

__all__ = [
    "PlayerPathOfLegendRanking",
    "PlayerRanking",
    "PlayerRankingClan",
]


class PlayerRankingClan(ClashRoyaleModel):
    """A clan in miniature, as it appears in rankings."""

    badge_id: int | None = None
    tag: str | None = None
    name: str | None = None
    badge_urls: BadgeUrls | None = None


class PlayerRanking(ClashRoyaleModel):
    """A player on a location or season leaderboard."""

    tag: str | None = None
    name: str | None = None
    exp_level: int | None = None
    rank: int | None = None
    previous_rank: int | None = None
    trophies: int | None = None
    clan: PlayerRankingClan | None = None
    arena: Arena | None = None


class PlayerPathOfLegendRanking(ClashRoyaleModel):
    """A player on a Path of Legend leaderboard."""

    tag: str | None = None
    name: str | None = None
    exp_level: int | None = None
    rank: int | None = None
    elo_rating: int | None = None
    clan: PlayerRankingClan | None = None
