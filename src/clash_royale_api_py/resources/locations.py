"""Locations and their leaderboards, plus league seasons."""

from __future__ import annotations

import builtins

from .._tags import tag_path_segment
from ..models import (
    ClanRanking,
    LadderTournamentRanking,
    LeagueSeason,
    Location,
    PlayerPathOfLegendRanking,
    PlayerRanking,
)
from ..pagination import AsyncPage, Page
from ._base import AsyncResource, Resource

__all__ = ["AsyncLocations", "Locations"]


class Locations(Resource):
    """Locations (countries and regions) and every leaderboard tied to them."""

    def list(
        self, *, limit: int | None = None, after: str | None = None, before: str | None = None
    ) -> Page[Location]:
        """List all available locations."""
        return self._fetch_page(
            "/locations",
            params={"limit": limit, "after": after, "before": before},
            model=Location,
        )

    def get(self, location_id: int) -> Location:
        """Get one location by id."""
        return self._fetch(f"/locations/{location_id}", model=Location)

    def clan_rankings(
        self,
        location_id: int,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[ClanRanking]:
        """Clan leaderboard for a location."""
        return self._fetch_page(
            f"/locations/{location_id}/rankings/clans",
            params={"limit": limit, "after": after, "before": before},
            model=ClanRanking,
        )

    def player_rankings(
        self,
        location_id: int,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[PlayerRanking]:
        """Player leaderboard for a location.

        Deprecated upstream: this always returns an empty list now. Use
        `path_of_legend_players` instead — kept here for completeness.
        """
        return self._fetch_page(
            f"/locations/{location_id}/rankings/players",
            params={"limit": limit, "after": after, "before": before},
            model=PlayerRanking,
        )

    def clan_war_rankings(
        self,
        location_id: int,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[ClanRanking]:
        """Clan war leaderboard for a location."""
        return self._fetch_page(
            f"/locations/{location_id}/rankings/clanwars",
            params={"limit": limit, "after": after, "before": before},
            model=ClanRanking,
        )

    def path_of_legend_players(
        self,
        location_id: int,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[PlayerPathOfLegendRanking]:
        """Path of Legend player rankings for a location."""
        return self._fetch_page(
            f"/locations/{location_id}/pathoflegend/players",
            params={"limit": limit, "after": after, "before": before},
            model=PlayerPathOfLegendRanking,
        )

    def path_of_legend_season_rankings(
        self,
        season_id: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[PlayerPathOfLegendRanking]:
        """Top Path of Legend players for a given season, globally."""
        return self._fetch_page(
            f"/locations/global/pathoflegend/{season_id}/rankings/players",
            params={"limit": limit, "after": after, "before": before},
            model=PlayerPathOfLegendRanking,
        )

    def league_seasons(self) -> builtins.list[LeagueSeason]:
        """List top-player league seasons."""
        return self._fetch_list("/locations/global/seasons", model=LeagueSeason)

    def league_seasons_v2(self) -> builtins.list[LeagueSeason]:
        """List league seasons with unique ids and end times."""
        return self._fetch_list("/locations/global/seasonsV2", model=LeagueSeason)

    def league_season(self, season_id: str) -> LeagueSeason:
        """Get one league season by id."""
        return self._fetch(f"/locations/global/seasons/{season_id}", model=LeagueSeason)

    def league_season_rankings(
        self,
        season_id: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[PlayerRanking]:
        """Top player rankings for a league season."""
        return self._fetch_page(
            f"/locations/global/seasons/{season_id}/rankings/players",
            params={"limit": limit, "after": after, "before": before},
            model=PlayerRanking,
        )

    def global_tournament_rankings(
        self,
        tournament_tag: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[LadderTournamentRanking]:
        """Rankings of a global tournament."""
        return self._fetch_page(
            f"/locations/global/rankings/tournaments/{tag_path_segment(tournament_tag)}",
            params={"limit": limit, "after": after, "before": before},
            model=LadderTournamentRanking,
        )


class AsyncLocations(AsyncResource):
    """Async counterpart of `Locations`."""

    async def list(
        self, *, limit: int | None = None, after: str | None = None, before: str | None = None
    ) -> AsyncPage[Location]:
        return await self._fetch_page(
            "/locations",
            params={"limit": limit, "after": after, "before": before},
            model=Location,
        )

    async def get(self, location_id: int) -> Location:
        return await self._fetch(f"/locations/{location_id}", model=Location)

    async def clan_rankings(
        self,
        location_id: int,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[ClanRanking]:
        return await self._fetch_page(
            f"/locations/{location_id}/rankings/clans",
            params={"limit": limit, "after": after, "before": before},
            model=ClanRanking,
        )

    async def player_rankings(
        self,
        location_id: int,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[PlayerRanking]:
        return await self._fetch_page(
            f"/locations/{location_id}/rankings/players",
            params={"limit": limit, "after": after, "before": before},
            model=PlayerRanking,
        )

    async def clan_war_rankings(
        self,
        location_id: int,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[ClanRanking]:
        return await self._fetch_page(
            f"/locations/{location_id}/rankings/clanwars",
            params={"limit": limit, "after": after, "before": before},
            model=ClanRanking,
        )

    async def path_of_legend_players(
        self,
        location_id: int,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[PlayerPathOfLegendRanking]:
        return await self._fetch_page(
            f"/locations/{location_id}/pathoflegend/players",
            params={"limit": limit, "after": after, "before": before},
            model=PlayerPathOfLegendRanking,
        )

    async def path_of_legend_season_rankings(
        self,
        season_id: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[PlayerPathOfLegendRanking]:
        return await self._fetch_page(
            f"/locations/global/pathoflegend/{season_id}/rankings/players",
            params={"limit": limit, "after": after, "before": before},
            model=PlayerPathOfLegendRanking,
        )

    async def league_seasons(self) -> builtins.list[LeagueSeason]:
        return await self._fetch_list("/locations/global/seasons", model=LeagueSeason)

    async def league_seasons_v2(self) -> builtins.list[LeagueSeason]:
        return await self._fetch_list("/locations/global/seasonsV2", model=LeagueSeason)

    async def league_season(self, season_id: str) -> LeagueSeason:
        return await self._fetch(f"/locations/global/seasons/{season_id}", model=LeagueSeason)

    async def league_season_rankings(
        self,
        season_id: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[PlayerRanking]:
        return await self._fetch_page(
            f"/locations/global/seasons/{season_id}/rankings/players",
            params={"limit": limit, "after": after, "before": before},
            model=PlayerRanking,
        )

    async def global_tournament_rankings(
        self,
        tournament_tag: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[LadderTournamentRanking]:
        return await self._fetch_page(
            f"/locations/global/rankings/tournaments/{tag_path_segment(tournament_tag)}",
            params={"limit": limit, "after": after, "before": before},
            model=LadderTournamentRanking,
        )
