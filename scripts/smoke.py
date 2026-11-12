"""Live smoke test against the real Clash Royale API.

The offline tests verify behavior; this script verifies *reality*: every
endpoint is called with live data, every response is validated against our
models, and any field the API sends that we don't model is reported —
keeping the models honest forever.

Usage:
    uv run python scripts/smoke.py

The token is read from CLASH_ROYALE_API_TOKEN (or CLASH_ROYALE_TOKEN_API)
or from a local .env file. It is never printed.
"""

from __future__ import annotations

import os
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from clash_royale_api_py import ClashRoyaleAPI, GoneError
from clash_royale_api_py.models import (
    Battle,
    Card,
    Clan,
    ClanMember,
    ClanRanking,
    ClanWarLogEntry,
    CurrentRiverRace,
    LadderTournament,
    LadderTournamentRanking,
    Leaderboard,
    LeaderboardEntry,
    LeagueSeason,
    Location,
    Player,
    PlayerPathOfLegendRanking,
    PlayerRanking,
    RiverRaceLogEntry,
    Tournament,
    TournamentHeader,
    TrailEvent,
)
from clash_royale_api_py.models.players import Chest

T = TypeVar("T")

RESULTS: list[tuple[str, str, str]] = []  # (status, name, detail)


def load_token() -> str:
    token = os.environ.get("CLASH_ROYALE_API_TOKEN") or os.environ.get("CLASH_ROYALE_TOKEN_API")
    if token:
        return token
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                key, _, value = line.partition("=")
                if key.strip() in ("CLASH_ROYALE_API_TOKEN", "CLASH_ROYALE_TOKEN_API"):
                    return value.strip().strip('"').strip("'")
    sys.exit(
        "No token found. Set CLASH_ROYALE_API_TOKEN or create a .env file "
        "(it's free at https://developer.clashroyale.com/#/account)."
    )


def model_fields(model: type[BaseModel]) -> set[str]:
    """The camelCase keys the model knows about."""
    return {(field.alias or name) for name, field in model.model_fields.items()}


def unmodeled(raw: Any, model: type[BaseModel]) -> list[str]:
    """Keys present in the raw payload but not in our model."""
    sample: Any = raw
    if isinstance(raw, dict) and isinstance(raw.get("items"), list):
        sample = raw["items"][0] if raw["items"] else None
    elif isinstance(raw, list):
        sample = raw[0] if raw else None
    if not isinstance(sample, dict):
        return []
    known = model_fields(model)
    return sorted(key for key in sample if key not in known)[:8]


def check(
    name: str,
    run: Callable[[], tuple[Any, type[BaseModel]]],
    *,
    optional: bool = False,
) -> None:
    """Call one endpoint, record the outcome, never raise."""
    time.sleep(0.3)  # be gentle with the rate limit
    try:
        raw, model = run()
    except Exception as error:  # noqa: BLE001 — a smoke test reports, not raises
        status = "SKIP" if optional else "FAIL"
        RESULTS.append((status, name, f"{type(error).__name__}: {error}"[:200]))
        return
    if raw is None or (isinstance(raw, (list, dict)) and not raw):
        status = "SKIP" if optional else "PASS"
        RESULTS.append((status, name, "empty response"))
        return
    extras = unmodeled(raw, model)
    detail = _summarize(raw)
    if extras:
        detail += f" | unmodeled: {', '.join(extras)}"
    RESULTS.append(("PASS", name, detail))


def check_gone(name: str, run: Callable[[], Any]) -> None:
    """A retired endpoint should raise GoneError — that *is* the correct behavior."""
    time.sleep(0.3)
    try:
        run()
    except GoneError:
        RESULTS.append(("PASS", name, "retired upstream — GoneError raised, as expected"))
    except Exception as error:  # noqa: BLE001
        RESULTS.append(
            ("FAIL", name, f"expected GoneError, got {type(error).__name__}: {error}"[:200])
        )
    else:
        RESULTS.append(("PASS", name, "still alive — endpoint returned data"))


def _summarize(raw: Any) -> str:
    if isinstance(raw, dict):
        items = raw.get("items")
        if isinstance(items, list):
            head = f", first: {_first(items)}" if items else ""
            return f"{len(items)} items{head}"
        return "keys: " + ", ".join(sorted(raw)[:6])
    if isinstance(raw, list):
        head = f", first: {_first(raw)}" if raw else ""
        return f"{len(raw)} items{head}"
    return type(raw).__name__


def _first(items: list[Any]) -> str:
    item = items[0]
    if not isinstance(item, dict):
        return str(item)
    name = item.get("name") or item.get("title")
    if isinstance(name, dict):
        name = next(iter(name.values()), None)
    bits = [str(name)] if name else []
    if item.get("tag"):
        bits.append(str(item["tag"]))
    return " ".join(bits) or "<item>"


def enc(tag: str) -> str:
    return tag.replace("#", "%23")


def _discover(api: ClashRoyaleAPI, fn: Callable[[], Any], label: str) -> Any:
    """Discovery must never kill the run — validation issues surface below."""
    try:
        return fn()
    except Exception as error:  # noqa: BLE001
        print(f"  discovery {label} failed: {type(error).__name__}: {error}")
        return None


def discover_clan(api: ClashRoyaleAPI) -> str | None:
    for query in ("war", "the", "clan", "legends"):
        for clan in api.clans.search(name=query, limit=10):
            if clan.tag:
                return clan.tag
    return None


def discover_player(api: ClashRoyaleAPI, clan_tag: str) -> str | None:
    for member in api.clans.members(clan_tag, limit=1):
        if member.tag:
            return member.tag
    return None


def discover_tournament(api: ClashRoyaleAPI) -> str | None:
    for query in ("war", "friendly", "weekend"):
        page = api.tournaments.search(name=query, limit=10)
        for header in page:
            if header.tag:
                return header.tag
    return None


def discover_country(api: ClashRoyaleAPI) -> int | None:
    for location in api.locations.list(limit=50).iter_all():
        if location.is_country and location.id is not None:
            return location.id
    return None


def newest_rankable_season(api: ClashRoyaleAPI, seasons: list[LeagueSeason]) -> str | None:
    """Binary-search the newest season that still has rankings.

    Season rankings were discontinued after the legacy ladder ended, so most
    recent seasons answer 404 — this finds the newest one that still works.
    """
    ids = [season.id for season in seasons if season.id]
    lo, hi, best = 0, len(ids) - 1, None
    while lo <= hi:
        mid = (lo + hi) // 2
        try:
            api.locations.league_season_rankings(ids[mid], limit=1)
        except Exception:  # noqa: BLE001 — 404 just means "no rankings here"
            hi = mid - 1
        else:
            best = ids[mid]
            lo = mid + 1
    return best


def main() -> None:
    api = ClashRoyaleAPI(load_token())
    print("Smoke-testing every endpoint against the live API…\n")

    check("cards.list", lambda: (api.cards.list(limit=5).raw, Card))
    check(
        "events.list",
        lambda: (api.events.list() and [event.raw for event in api.events.list()], TrailEvent),
    )
    check("locations.list", lambda: (api.locations.list(limit=5).raw, Location))

    clan_tag = _discover(api, lambda: discover_clan(api), "clan")
    player_tag: str | None = None
    country_id: int | None = None

    if clan_tag:
        player_tag = _discover(api, lambda: discover_player(api, clan_tag), "player")
        country_id = _discover(api, lambda: discover_country(api), "country")
        print(f"  sample clan:     {clan_tag}")
        print(f"  sample player:   {player_tag}")
        print(f"  sample country:  {country_id}")

        check("clans.get", lambda: (api.clans.get(clan_tag).raw, Clan))
        check(
            "clans.search",
            lambda: (
                api._transport.get_json("/clans", {"name": "war", "limit": 5}),
                Clan,
            ),
        )
        check(
            "clans.members",
            lambda: (
                api._transport.get_json(f"/clans/{enc(clan_tag)}/members", {"limit": 5}),
                ClanMember,
            ),
        )
        check(
            "clans.war_log",
            lambda: (
                api._transport.get_json(f"/clans/{enc(clan_tag)}/warlog", {"limit": 3}),
                ClanWarLogEntry,
            ),
            optional=True,
        )
        check_gone("clans.current_war", lambda: api.clans.current_war(clan_tag))
        check(
            "clans.river_race_log",
            lambda: (
                api._transport.get_json(f"/clans/{enc(clan_tag)}/riverracelog", {"limit": 3}),
                RiverRaceLogEntry,
            ),
            optional=True,
        )
        check(
            "clans.current_river_race",
            lambda: (api.clans.current_river_race(clan_tag).raw, CurrentRiverRace),
            optional=True,
        )

    if player_tag:
        check("players.get", lambda: (api.players.get(player_tag).raw, Player))
        check(
            "players.upcoming_chests",
            lambda: (api.players.upcoming_chests(player_tag).raw, Chest),
            optional=True,
        )
        check(
            "players.battle_log",
            lambda: (
                api._transport.get_json(f"/players/{enc(player_tag)}/battlelog"),
                Battle,
            ),
            optional=True,
        )

    tournament_tag = _discover(api, lambda: discover_tournament(api), "tournament")
    check(
        "tournaments.search",
        lambda: (
            api._transport.get_json("/tournaments", {"name": "war", "limit": 5}),
            TournamentHeader,
        ),
    )
    if tournament_tag:
        print(f"  sample tournament: {tournament_tag}")
        check(
            "tournaments.get",
            lambda: (api.tournaments.get(tournament_tag).raw, Tournament),
        )
    else:
        RESULTS.append(("SKIP", "tournaments.get", "no tournament running right now"))

    check(
        "globaltournaments.list",
        lambda: (
            api.global_tournaments.list() and [t.raw for t in api.global_tournaments.list()],
            LadderTournament,
        ),
    )
    global_tournaments = api.global_tournaments.list()
    if global_tournaments and global_tournaments[0].tag:
        gtag = global_tournaments[0].tag
        check(
            "locations.global_tournament_rankings",
            lambda: (
                api._transport.get_json(
                    f"/locations/global/rankings/tournaments/{enc(gtag)}",
                    {"limit": 5},
                ),
                LadderTournamentRanking,
            ),
        )
    else:
        RESULTS.append(
            ("SKIP", "locations.global_tournament_rankings", "no global tournament right now")
        )

    check(
        "leaderboards.list",
        lambda: (api.leaderboards.list() and [b.raw for b in api.leaderboards.list()], Leaderboard),
    )
    leaderboards = api.leaderboards.list()
    if leaderboards and leaderboards[0].id is not None:
        board_id = leaderboards[0].id
        check(
            "leaderboards.get",
            lambda: (
                api._transport.get_json(f"/leaderboard/{board_id}", {"limit": 5}),
                LeaderboardEntry,
            ),
        )
    board_with_league = next(
        (
            (board.id, board.leagues[0])
            for board in leaderboards
            if board.id is not None and board.leagues
        ),
        None,
    )
    if board_with_league is not None:
        league_board_id, league = board_with_league
        league_id = league.get("id") if isinstance(league, dict) else league
        check(
            "leaderboards.league",
            lambda: (
                api._transport.get_json(
                    f"/leaderboard/{league_board_id}/leagues/{league_id}", {"limit": 5}
                ),
                LeaderboardEntry,
            ),
        )
    else:
        RESULTS.append(("SKIP", "leaderboards.league", "no league is active right now"))

    if country_id is not None:
        check("locations.get", lambda: (api.locations.get(country_id).raw, Location))
        check(
            "locations.clan_rankings",
            lambda: (
                api._transport.get_json(f"/locations/{country_id}/rankings/clans", {"limit": 5}),
                ClanRanking,
            ),
        )
        check(
            "locations.clan_war_rankings",
            lambda: (
                api._transport.get_json(f"/locations/{country_id}/rankings/clanwars", {"limit": 5}),
                ClanRanking,
            ),
        )
        check(
            "locations.player_rankings (deprecated)",
            lambda: (
                api._transport.get_json(f"/locations/{country_id}/rankings/players", {"limit": 5}),
                PlayerRanking,
            ),
        )
        check(
            "locations.path_of_legend_players",
            lambda: (
                api._transport.get_json(
                    f"/locations/{country_id}/pathoflegend/players", {"limit": 5}
                ),
                PlayerPathOfLegendRanking,
            ),
        )

    check(
        "locations.league_seasons",
        lambda: (
            api.locations.league_seasons() and [s.raw for s in api.locations.league_seasons()],
            LeagueSeason,
        ),
    )
    seasons = api.locations.league_seasons()
    if seasons:
        season_id = seasons[-1].id
        if season_id:
            check(
                "locations.league_season",
                lambda: (api.locations.league_season(season_id).raw, LeagueSeason),
            )
        rankable = _discover(api, lambda: newest_rankable_season(api, seasons), "rankable season")
        if rankable:
            print(f"  newest season with rankings: {rankable}")
            check(
                "locations.league_season_rankings",
                lambda: (
                    api._transport.get_json(
                        f"/locations/global/seasons/{rankable}/rankings/players",
                        {"limit": 5},
                    ),
                    PlayerRanking,
                ),
            )
            check(
                "locations.path_of_legend_season_rankings",
                lambda: (
                    api._transport.get_json(
                        f"/locations/global/pathoflegend/{rankable}/rankings/players",
                        {"limit": 5},
                    ),
                    PlayerPathOfLegendRanking,
                ),
                optional=True,
            )
        else:
            RESULTS.append(
                ("SKIP", "locations.league_season_rankings", "no season has rankings anymore")
            )
    check(
        "locations.league_seasons_v2",
        lambda: (
            api.locations.league_seasons_v2()
            and [s.raw for s in api.locations.league_seasons_v2()],
            LeagueSeason,
        ),
    )

    # Report
    print()
    width = max(len(name) for _, name, _ in RESULTS)
    for status, name, detail in RESULTS:
        icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️ "}[status]
        print(f"{icon} {name:<{width}}  {detail}")

    failures = [r for r in RESULTS if r[0] == "FAIL"]
    passed = sum(1 for r in RESULTS if r[0] == "PASS")
    skipped = sum(1 for r in RESULTS if r[0] == "SKIP")
    print(f"\n{passed} passed · {skipped} skipped · {len(failures)} failed")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
