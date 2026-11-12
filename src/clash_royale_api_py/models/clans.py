"""Clan models: rosters, wars, and river races."""

from __future__ import annotations

from ._base import ClashRoyaleModel
from .common import Arena, BadgeUrls, Location

__all__ = [
    "Clan",
    "ClanMember",
    "ClanRanking",
    "ClanWarClan",
    "ClanWarLogEntry",
    "ClanWarParticipant",
    "ClanWarStanding",
    "CurrentClanWar",
    "CurrentRiverRace",
    "PeriodLog",
    "PeriodLogEntry",
    "RiverRaceClan",
    "RiverRaceLogEntry",
    "RiverRaceParticipant",
    "RiverRaceStanding",
]


class ClanMember(ClashRoyaleModel):
    """A single member of a clan."""

    tag: str | None = None
    name: str | None = None
    role: str | None = None
    exp_level: int | None = None
    trophies: int | None = None
    clan_rank: int | None = None
    previous_clan_rank: int | None = None
    donations: int | None = None
    donations_received: int | None = None
    clan_chest_points: int | None = None
    last_seen: str | None = None
    arena: Arena | None = None

    def __repr__(self) -> str:
        return f"<ClanMember {self.name!r} {self.trophies!r} trophies>"


class Clan(ClashRoyaleModel):
    """A clan: its roster, its score, and everything public about it."""

    tag: str | None = None
    name: str | None = None
    description: str | None = None
    type: str | None = None  # OPEN, INVITE_ONLY, CLOSED
    badge_id: int | None = None
    badge_urls: BadgeUrls | None = None
    clan_score: int | None = None
    clan_war_trophies: int | None = None
    location: Location | None = None
    required_trophies: int | None = None
    donations_per_week: int | None = None
    members: int | None = None  # member count
    clan_chest_status: str | None = None
    clan_chest_level: int | None = None
    clan_chest_max_level: int | None = None
    clan_chest_points: int | None = None
    member_list: list[ClanMember] | None = None

    def __repr__(self) -> str:
        return f"<Clan {self.name!r} tag={self.tag!r} members={self.members!r}>"


class ClanRanking(ClashRoyaleModel):
    """A clan as it appears on a location's leaderboard."""

    badge_id: int | None = None
    clan_score: int | None = None
    members: int | None = None
    location: Location | None = None
    tag: str | None = None
    name: str | None = None
    rank: int | None = None
    previous_rank: int | None = None
    badge_urls: BadgeUrls | None = None


class ClanWarClan(ClashRoyaleModel):
    """A clan taking part in a classic clan war."""

    crowns: int | None = None
    badge_id: int | None = None
    clan_score: int | None = None
    name: str | None = None
    tag: str | None = None
    participants: int | None = None
    battles_played: int | None = None
    wins: int | None = None


class ClanWarParticipant(ClashRoyaleModel):
    """One player's contribution to a clan war."""

    tag: str | None = None
    name: str | None = None
    cards_earned: int | None = None
    battles_played: int | None = None
    wins: int | None = None
    collection_day_battles_played: int | None = None
    number_of_battles: int | None = None


class ClanWarStanding(ClashRoyaleModel):
    """A clan's standing in a clan war entry."""

    trophy_change: int | None = None
    clan: ClanWarClan | None = None


class ClanWarLogEntry(ClashRoyaleModel):
    """One war in a clan's war log."""

    standings: list[ClanWarStanding] | None = None
    season_id: int | None = None
    participants: list[ClanWarParticipant] | None = None
    created_date: str | None = None


class CurrentClanWar(ClashRoyaleModel):
    """The clan war happening right now — ``None``-ish state if not in one.

    Check ``war.state`` first: ``NOT_IN_WAR`` is a perfectly common answer.
    """

    state: str | None = None  # NOT_IN_WAR, COLLECTION_DAY, WAR_DAY, ...
    clan: ClanWarClan | None = None
    participants: list[ClanWarParticipant] | None = None
    clans: list[ClanWarClan] | None = None
    collection_end_time: str | None = None
    war_end_time: str | None = None

    @property
    def is_in_war(self) -> bool:
        """Whether the clan is currently part of a war at all."""
        return self.state not in (None, "CLAN_NOT_FOUND", "ACCESS_DENIED", "NOT_IN_WAR")


class RiverRaceParticipant(ClashRoyaleModel):
    """One player's contribution to a river race."""

    tag: str | None = None
    name: str | None = None
    fame: int | None = None
    repair_points: int | None = None
    boat_attacks: int | None = None
    decks_used: int | None = None
    decks_used_today: int | None = None


class RiverRaceClan(ClashRoyaleModel):
    """A clan taking part in a river race (Clan Wars 2)."""

    badge_id: int | None = None
    clan_score: int | None = None
    name: str | None = None
    tag: str | None = None
    fame: int | None = None
    repair_points: int | None = None
    finish_time: str | None = None
    participants: list[RiverRaceParticipant] | None = None
    period_points: int | None = None

    @property
    def points(self) -> int:
        """The number to sort by during a race.

        Mid-race the API reports ``fame`` as 0 and keeps the live score in
        ``period_points``; after the race the two coincide.
        """
        return self.period_points or self.fame or 0


class RiverRaceStanding(ClashRoyaleModel):
    """A clan's standing in a river race week."""

    rank: int | None = None
    trophy_change: int | None = None
    clan: RiverRaceClan | None = None


class RiverRaceLogEntry(ClashRoyaleModel):
    """One week of a clan's river race history."""

    standings: list[RiverRaceStanding] | None = None
    season_id: int | None = None
    created_date: str | None = None
    section_index: int | None = None


class PeriodLogEntry(ClashRoyaleModel):
    """One day's progress inside a river race period."""


class PeriodLog(ClashRoyaleModel):
    """A river race period's progress log."""

    period_index: int | None = None
    items: list[PeriodLogEntry] | None = None


class CurrentRiverRace(ClashRoyaleModel):
    """The river race happening right now."""

    state: str | None = None  # MATCHMAKING, MATCHED, FULL, ENDED, ...
    clan: RiverRaceClan | None = None
    clans: list[RiverRaceClan] | None = None
    collection_end_time: str | None = None
    war_end_time: str | None = None
    section_index: int | None = None
    period_index: int | None = None
    period_type: str | None = None  # TRAINING, WAR_DAY, COLOSSEUM
    period_logs: list[PeriodLog] | None = None

    @property
    def our_clan(self) -> RiverRaceClan | None:
        """The requested clan, picked out of the race standings."""
        return self.clan
