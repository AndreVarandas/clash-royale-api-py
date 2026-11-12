"""Player models: profiles, battles, and upcoming chests."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from ._base import ClashRoyaleModel
from .common import Arena, BadgeUrls, GameMode, JsonLocalizedName

__all__ = [
    "Battle",
    "Chest",
    "Player",
    "PlayerAchievementBadge",
    "PlayerAchievementProgress",
    "PlayerBattleData",
    "PlayerBattleRound",
    "PlayerClan",
    "PlayerItemLevel",
    "PlayerLeagueStatistics",
    "PlayerProgress",
    "PathOfLegendSeasonResult",
    "LeagueSeasonResult",
    "UpcomingChests",
]


class PlayerClan(ClashRoyaleModel):
    """The clan a player belongs to, in miniature."""

    badge_id: int | None = None
    tag: str | None = None
    name: str | None = None
    badge_urls: BadgeUrls | None = None


class PlayerItemLevel(ClashRoyaleModel):
    """A card in a player's collection or deck, with its level."""

    id: int | None = None
    name: str | JsonLocalizedName | None = None
    rarity: str | None = None
    count: int | None = None
    level: int | None = None
    star_level: int | None = None
    evolution_level: int | None = None
    max_level: int | None = None
    elixir_cost: int | None = None
    max_evolution_level: int | None = None
    used: bool | None = None
    icon_urls: dict[str, Any] | None = None


class PlayerBattleRound(ClashRoyaleModel):
    """One round inside a battle."""


class PlayerBattleData(ClashRoyaleModel):
    """One player's side of a battle."""

    tag: str | None = None
    name: str | None = None
    crowns: int | None = None
    king_tower_hit_points: int | None = None
    princess_towers_hit_points: list[int] | None = None
    elixir_leaked: float | None = None
    global_rank: int | None = None
    starting_trophies: int | None = None
    trophy_change: int | None = None
    clan: PlayerClan | None = None
    cards: list[PlayerItemLevel] | None = None
    support_cards: list[PlayerItemLevel] | None = None
    rounds: list[PlayerBattleRound] | None = None


class PlayerBattleAugment(ClashRoyaleModel):
    """A battle modifier applied to one side."""


class Battle(ClashRoyaleModel):
    """One recent battle from a player's battle log."""

    type: str | None = None  # PVP, RIVER_RACE_PVP, PATH_OF_LEGEND, ...
    battle_time: str | None = None
    arena: Arena | None = None
    game_mode: GameMode | None = None
    team: list[PlayerBattleData] | None = None
    opponent: list[PlayerBattleData] | None = None
    league_number: int | None = None
    tournament_tag: str | None = None
    tournament_title: str | None = None
    challenge_title: str | None = None
    challenge_id: int | None = None
    challenge_win_count_before: int | None = None
    deck_selection: str | None = None
    is_ladder_tournament: bool | None = None
    is_hosted_match: bool | None = None
    event_tag: str | None = None
    boat_battle_side: str | None = None
    boat_battle_won: bool | None = None
    new_towers_destroyed: int | None = None
    prev_towers_destroyed: int | None = None
    remaining_towers: int | None = None
    modifiers: list[PlayerBattleAugment] | None = None

    @property
    def crowns_for(self) -> int | None:
        """Crowns earned by the requested player (first member of ``team``)."""
        return self.team[0].crowns if self.team else None

    @property
    def crowns_against(self) -> int | None:
        """Crowns earned by the opponent (first member of ``opponent``)."""
        return self.opponent[0].crowns if self.opponent else None

    @property
    def trophy_change(self) -> int | None:
        """Trophy delta for the requested player, when this was a trophy battle."""
        return self.team[0].trophy_change if self.team else None


class LeagueSeasonResult(ClashRoyaleModel):
    """A player's result in one league season."""

    best_trophies: int | None = None
    rank: int | None = None
    id: str | None = None
    trophies: int | None = None


class PathOfLegendSeasonResult(ClashRoyaleModel):
    """A player's result in one Path of Legend season."""

    rank: int | None = None
    league_number: int | None = None
    trophies: int | None = None


class PlayerLeagueStatistics(ClashRoyaleModel):
    """The player's league history across seasons."""

    current_season: LeagueSeasonResult | None = None
    previous_season: LeagueSeasonResult | None = None
    best_season: LeagueSeasonResult | None = None


class PlayerProgress(ClashRoyaleModel):
    """A player's progress in one game mode / season track.

    ``arena`` is where they currently stand, with their trophy count and
    personal best for that track.
    """

    arena: Arena | None = None
    trophies: int | None = None
    best_trophies: int | None = None


class PlayerAchievementProgress(ClashRoyaleModel):
    """Progress towards a player achievement."""


class PlayerAchievementBadge(ClashRoyaleModel):
    """A badge earned by a player."""

    progress: int | None = None
    max_level: int | None = None
    target: int | None = None
    level: int | None = None
    name: str | None = None
    icon_urls: dict[str, Any] | None = None


class Player(ClashRoyaleModel):
    """A player profile: stats, deck, badges, and clan."""

    tag: str | None = None
    name: str | None = None
    exp_level: int | None = None
    trophies: int | None = None
    best_trophies: int | None = None
    wins: int | None = None
    losses: int | None = None
    battle_count: int | None = None
    three_crown_wins: int | None = None
    challenge_cards_won: int | None = None
    challenge_max_wins: int | None = None
    tournament_cards_won: int | None = None
    tournament_battle_count: int | None = None
    role: str | None = None  # MEMBER, LEADER, ADMIN, COLEADER...
    donations: int | None = None
    donations_received: int | None = None
    total_donations: int | None = None
    war_day_wins: int | None = None
    clan_cards_collected: int | None = None
    clan: PlayerClan | None = None
    arena: Arena | None = None
    league_statistics: PlayerLeagueStatistics | None = None
    badges: list[PlayerAchievementBadge] | None = None
    achievements: list[PlayerAchievementProgress] | None = None
    cards: list[PlayerItemLevel] | None = None
    support_cards: list[PlayerItemLevel] | None = None
    current_deck: list[PlayerItemLevel] | None = None
    current_deck_support_cards: list[PlayerItemLevel] | None = None
    current_favourite_card: PlayerItemLevel | None = None
    current_path_of_legend_season_result: PathOfLegendSeasonResult | None = None
    last_path_of_legend_season_result: PathOfLegendSeasonResult | None = None
    best_path_of_legend_season_result: PathOfLegendSeasonResult | None = None
    star_points: int | None = None
    exp_points: int | None = None
    total_exp_points: int | None = None
    collection_level: int | None = None
    king_tower_level: int | None = None
    current_win_lose_streak: int | None = None
    legacy_trophy_road_high_score: int | None = None
    progress: dict[str, PlayerProgress] | None = None

    def __repr__(self) -> str:
        return f"<Player {self.name!r} tag={self.tag!r} {self.trophies!r} trophies>"


class Chest(ClashRoyaleModel):
    """An upcoming reward chest."""

    name: str | JsonLocalizedName | None = None
    index: int | None = None
    icon_urls: dict[str, Any] | None = None


class UpcomingChests(ClashRoyaleModel):
    """The chests a player will open next, in order."""

    items: list[Chest] | None = None

    def __iter__(self) -> Iterator[Chest]:  # type: ignore[override]
        return iter(self.items or [])

    def __len__(self) -> int:
        return len(self.items or [])

    def __getitem__(self, index: int) -> Chest:
        return (self.items or [])[index]
