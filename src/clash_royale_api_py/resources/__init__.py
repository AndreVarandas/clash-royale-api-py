"""Resource classes: the public surface of the API."""

from __future__ import annotations

from .cards import AsyncCards, AsyncEvents, Cards, Events
from .clans import AsyncClans, Clans
from .leaderboards import AsyncLeaderboards, Leaderboards
from .locations import AsyncLocations, Locations
from .players import AsyncPlayers, Players
from .raw import AsyncRaw, Raw
from .tournaments import (
    AsyncGlobalTournaments,
    AsyncTournaments,
    GlobalTournaments,
    Tournaments,
)

__all__ = [
    "AsyncCards",
    "AsyncClans",
    "AsyncEvents",
    "AsyncGlobalTournaments",
    "AsyncLeaderboards",
    "AsyncLocations",
    "AsyncPlayers",
    "AsyncRaw",
    "AsyncTournaments",
    "Cards",
    "Clans",
    "Events",
    "GlobalTournaments",
    "Leaderboards",
    "Locations",
    "Players",
    "Raw",
    "Tournaments",
]
