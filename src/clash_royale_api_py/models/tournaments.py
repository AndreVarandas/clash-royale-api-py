"""Tournament models: searchable tournaments and global ladder tournaments."""

from __future__ import annotations

from ._base import ClashRoyaleModel
from .common import GameMode, JsonLocalizedName
from .players import PlayerClan

__all__ = [
    "LadderTournament",
    "LadderTournamentRanking",
    "SurvivalMilestoneReward",
    "Tournament",
    "TournamentHeader",
    "TournamentMember",
]


class TournamentMember(ClashRoyaleModel):
    """A player in a tournament, with their score."""

    tag: str | None = None
    name: str | None = None
    score: int | None = None
    rank: int | None = None
    previous_rank: int | None = None
    clan: PlayerClan | None = None


class Tournament(ClashRoyaleModel):
    """A full tournament, members included."""

    tag: str | None = None
    name: str | None = None
    description: str | None = None
    status: str | None = None  # IN_PREPARATION, IN_PROGRESS, ENDED
    type: str | None = None  # OPEN, PASSWORD_PROTECTED
    created_time: str | None = None
    started_time: str | None = None
    ended_time: str | None = None
    preparation_duration: int | None = None
    duration: int | None = None
    capacity: int | None = None
    max_capacity: int | None = None
    level_cap: int | None = None
    first_place_card_prize: int | None = None
    game_mode: GameMode | None = None
    members_list: list[TournamentMember] | None = None

    def __repr__(self) -> str:
        return f"<Tournament {self.name!r} tag={self.tag!r} status={self.status!r}>"


class TournamentHeader(ClashRoyaleModel):
    """A tournament as it appears in search results."""

    tag: str | None = None
    name: str | None = None
    description: str | None = None
    status: str | None = None
    type: str | None = None
    created_time: str | None = None
    started_time: str | None = None
    ended_time: str | None = None
    preparation_duration: int | None = None
    duration: int | None = None
    capacity: int | None = None
    max_capacity: int | None = None
    level_cap: int | None = None
    first_place_card_prize: int | None = None
    game_mode: GameMode | None = None


class SurvivalMilestoneReward(ClashRoyaleModel):
    """A reward granted at a milestone of a global tournament."""

    chest: str | None = None
    rarity: str | None = None
    resource: str | None = None
    type: str | None = None
    amount: int | None = None
    consumable_name: str | None = None
    wins: int | None = None


class LadderTournament(ClashRoyaleModel):
    """A global tournament everybody can join."""

    tag: str | None = None
    title: str | JsonLocalizedName | None = None
    start_time: str | None = None
    end_time: str | None = None
    game_mode: GameMode | None = None
    max_losses: int | None = None
    tournament_level: int | None = None
    min_exp_level: int | None = None
    max_top_reward_rank: int | None = None
    milestone_rewards: list[SurvivalMilestoneReward] | None = None
    free_tier_rewards: list[SurvivalMilestoneReward] | None = None
    top_rank_reward: list[SurvivalMilestoneReward] | None = None


class LadderTournamentRanking(ClashRoyaleModel):
    """A player's standing in a global tournament."""

    tag: str | None = None
    name: str | None = None
    rank: int | None = None
    previous_rank: int | None = None
    wins: int | None = None
    losses: int | None = None
