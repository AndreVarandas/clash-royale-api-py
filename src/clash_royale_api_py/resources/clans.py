"""Clans: search them, inspect them, and follow their wars and river races."""

from __future__ import annotations

from .._tags import tag_path_segment
from ..models import (
    Clan,
    ClanMember,
    ClanWarLogEntry,
    CurrentClanWar,
    CurrentRiverRace,
    RiverRaceLogEntry,
)
from ..pagination import AsyncPage, Page
from ._base import AsyncResource, Resource

__all__ = ["AsyncClans", "Clans"]


class Clans(Resource):
    """Everything about clans."""

    def get(self, tag: str) -> Clan:
        """Get a clan by tag — ``"#2PP"``, ``"2PP"``, whatever you have."""
        return self._fetch(f"/clans/{tag_path_segment(tag)}", model=Clan)

    def search(
        self,
        *,
        name: str | None = None,
        location_id: int | None = None,
        min_members: int | None = None,
        max_members: int | None = None,
        min_score: int | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[Clan]:
        """Search clans by name and/or filters.

        ``name`` must be at least three characters; it matches anywhere in
        the clan name. Returns a `Page` you can iterate — pass
        ``.iter_all()`` to keep going across pages.
        """
        return self._fetch_page(
            "/clans",
            params={
                "name": name,
                "locationId": location_id,
                "minMembers": min_members,
                "maxMembers": max_members,
                "minScore": min_score,
                "limit": limit,
                "after": after,
                "before": before,
            },
            model=Clan,
        )

    def members(
        self,
        tag: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[ClanMember]:
        """List a clan's members, as an iterable `Page`."""
        return self._fetch_page(
            f"/clans/{tag_path_segment(tag)}/members",
            params={"limit": limit, "after": after, "before": before},
            model=ClanMember,
        )

    def war_log(
        self,
        tag: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[ClanWarLogEntry]:
        """The clan's war history, newest first."""
        return self._fetch_page(
            f"/clans/{tag_path_segment(tag)}/warlog",
            params={"limit": limit, "after": after, "before": before},
            model=ClanWarLogEntry,
        )

    def current_war(self, tag: str) -> CurrentClanWar:
        """The clan's current (classic) war — check ``.state``, ``NOT_IN_WAR`` is common.

        .. deprecated:: upstream
            Classic clan wars were retired: the API now answers **410 Gone**
            for this endpoint, so calling this raises `GoneError`.
            Use `current_river_race` instead.
        """
        return self._fetch(f"/clans/{tag_path_segment(tag)}/currentwar", model=CurrentClanWar)

    def river_race_log(
        self,
        tag: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Page[RiverRaceLogEntry]:
        """The clan's river race (Clan Wars 2) history, week by week."""
        return self._fetch_page(
            f"/clans/{tag_path_segment(tag)}/riverracelog",
            params={"limit": limit, "after": after, "before": before},
            model=RiverRaceLogEntry,
        )

    def current_river_race(self, tag: str) -> CurrentRiverRace:
        """The clan's current river race."""
        return self._fetch(
            f"/clans/{tag_path_segment(tag)}/currentriverrace", model=CurrentRiverRace
        )


class AsyncClans(AsyncResource):
    """Async counterpart of `Clans`: same methods, awaited."""

    async def get(self, tag: str) -> Clan:
        return await self._fetch(f"/clans/{tag_path_segment(tag)}", model=Clan)

    async def search(
        self,
        *,
        name: str | None = None,
        location_id: int | None = None,
        min_members: int | None = None,
        max_members: int | None = None,
        min_score: int | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[Clan]:
        return await self._fetch_page(
            "/clans",
            params={
                "name": name,
                "locationId": location_id,
                "minMembers": min_members,
                "maxMembers": max_members,
                "minScore": min_score,
                "limit": limit,
                "after": after,
                "before": before,
            },
            model=Clan,
        )

    async def members(
        self,
        tag: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[ClanMember]:
        return await self._fetch_page(
            f"/clans/{tag_path_segment(tag)}/members",
            params={"limit": limit, "after": after, "before": before},
            model=ClanMember,
        )

    async def war_log(
        self,
        tag: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[ClanWarLogEntry]:
        return await self._fetch_page(
            f"/clans/{tag_path_segment(tag)}/warlog",
            params={"limit": limit, "after": after, "before": before},
            model=ClanWarLogEntry,
        )

    async def current_war(self, tag: str) -> CurrentClanWar:
        return await self._fetch(f"/clans/{tag_path_segment(tag)}/currentwar", model=CurrentClanWar)

    async def river_race_log(
        self,
        tag: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> AsyncPage[RiverRaceLogEntry]:
        return await self._fetch_page(
            f"/clans/{tag_path_segment(tag)}/riverracelog",
            params={"limit": limit, "after": after, "before": before},
            model=RiverRaceLogEntry,
        )

    async def current_river_race(self, tag: str) -> CurrentRiverRace:
        return await self._fetch(
            f"/clans/{tag_path_segment(tag)}/currentriverrace", model=CurrentRiverRace
        )
