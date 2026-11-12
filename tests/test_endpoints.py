"""Every endpoint, one table: paths and query params must match the contract.

The smoke test proves the API accepts us; this proves we always call the
right address. One catch-all route answers every request, then we inspect
what actually went over the wire.
"""

from __future__ import annotations

import pytest

BASE = "/v1"

CASES = [
    # (id, call, expected raw path, expected query params)
    ("clans.get", lambda api: api.clans.get("2PP"), "/v1/clans/%232PP", {}),
    (
        "clans.search",
        lambda api: api.clans.search(name="war", min_members=10, min_score=500, limit=5),
        "/v1/clans",
        {"name": "war", "minMembers": "10", "minScore": "500", "limit": "5"},
    ),
    (
        "clans.members",
        lambda api: api.clans.members("2PP", limit=5),
        "/v1/clans/%232PP/members",
        {"limit": "5"},
    ),
    (
        "clans.war_log",
        lambda api: api.clans.war_log("2PP"),
        "/v1/clans/%232PP/warlog",
        {},
    ),
    (
        "clans.current_war",
        lambda api: api.clans.current_war("2PP"),
        "/v1/clans/%232PP/currentwar",
        {},
    ),
    (
        "clans.river_race_log",
        lambda api: api.clans.river_race_log("2PP"),
        "/v1/clans/%232PP/riverracelog",
        {},
    ),
    (
        "clans.current_river_race",
        lambda api: api.clans.current_river_race("2PP"),
        "/v1/clans/%232PP/currentriverrace",
        {},
    ),
    ("players.get", lambda api: api.players.get("2PP"), "/v1/players/%232PP", {}),
    (
        "players.upcoming_chests",
        lambda api: api.players.upcoming_chests("2PP"),
        "/v1/players/%232PP/upcomingchests",
        {},
    ),
    (
        "players.battle_log",
        lambda api: api.players.battle_log("2PP"),
        "/v1/players/%232PP/battlelog",
        {},
    ),
    ("cards.list", lambda api: api.cards.list(limit=5), "/v1/cards", {"limit": "5"}),
    ("cards.all", lambda api: api.cards.all(), "/v1/cards", {}),
    ("events.list", lambda api: api.events.list(), "/v1/events", {}),
    (
        "tournaments.search",
        lambda api: api.tournaments.search(name="war"),
        "/v1/tournaments",
        {"name": "war"},
    ),
    (
        "tournaments.get",
        lambda api: api.tournaments.get("2PP"),
        "/v1/tournaments/%232PP",
        {},
    ),
    (
        "global_tournaments.list",
        lambda api: api.global_tournaments.list(),
        "/v1/globaltournaments",
        {},
    ),
    ("locations.list", lambda api: api.locations.list(limit=5), "/v1/locations", {"limit": "5"}),
    ("locations.get", lambda api: api.locations.get(57000007), "/v1/locations/57000007", {}),
    (
        "locations.clan_rankings",
        lambda api: api.locations.clan_rankings(57000007),
        "/v1/locations/57000007/rankings/clans",
        {},
    ),
    (
        "locations.player_rankings",
        lambda api: api.locations.player_rankings(57000007),
        "/v1/locations/57000007/rankings/players",
        {},
    ),
    (
        "locations.clan_war_rankings",
        lambda api: api.locations.clan_war_rankings(57000007),
        "/v1/locations/57000007/rankings/clanwars",
        {},
    ),
    (
        "locations.path_of_legend_players",
        lambda api: api.locations.path_of_legend_players(57000007),
        "/v1/locations/57000007/pathoflegend/players",
        {},
    ),
    (
        "locations.path_of_legend_season_rankings",
        lambda api: api.locations.path_of_legend_season_rankings("2022-09"),
        "/v1/locations/global/pathoflegend/2022-09/rankings/players",
        {},
    ),
    (
        "locations.league_seasons",
        lambda api: api.locations.league_seasons(),
        "/v1/locations/global/seasons",
        {},
    ),
    (
        "locations.league_seasons_v2",
        lambda api: api.locations.league_seasons_v2(),
        "/v1/locations/global/seasonsV2",
        {},
    ),
    (
        "locations.league_season",
        lambda api: api.locations.league_season("2022-09"),
        "/v1/locations/global/seasons/2022-09",
        {},
    ),
    (
        "locations.league_season_rankings",
        lambda api: api.locations.league_season_rankings("2022-09"),
        "/v1/locations/global/seasons/2022-09/rankings/players",
        {},
    ),
    (
        "locations.global_tournament_rankings",
        lambda api: api.locations.global_tournament_rankings("2PP"),
        "/v1/locations/global/rankings/tournaments/%232PP",
        {},
    ),
    ("leaderboards.list", lambda api: api.leaderboards.list(), "/v1/leaderboards", {}),
    ("leaderboards.get", lambda api: api.leaderboards.get(0), "/v1/leaderboard/0", {}),
    (
        "leaderboards.league",
        lambda api: api.leaderboards.league(0, 1),
        "/v1/leaderboard/0/leagues/1",
        {},
    ),
    ("raw.get", lambda api: api.raw.get("/anything/else"), "/v1/anything/else", {}),
]


@pytest.mark.parametrize(
    ("call", "expected_path", "expected_params"),
    [case[1:] for case in CASES],
    ids=[case[0] for case in CASES],
)
def test_endpoint_calls_the_right_address(api, router, call, expected_path, expected_params):
    route = router.route().respond(json={})

    call(api)

    request = route.calls[-1].request
    raw_path = request.url.raw_path.partition(b"?")[0].decode()
    assert raw_path == expected_path
    assert str(request.headers["Authorization"]) == "Bearer test-token"
    params = request.url.params
    for key, value in expected_params.items():
        assert params[key] == value
