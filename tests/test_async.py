"""The async client mirrors the sync client, with ``await`` in front."""

from __future__ import annotations

import httpx
import pytest

from clash_royale_api_py.exceptions import NotFoundError
from tests.conftest import CLAN_JSON, MEMBER_JSON


async def test_get_clan(aapi, router):
    route = router.get("/clans/%232PP").respond(json=CLAN_JSON)
    clan = await aapi.clans.get("#2PP")
    assert clan.name == "Wars R Us"
    assert route.called


async def test_not_found(aapi, router):
    router.get("/clans/%23000").respond(status_code=404, json={"reason": "notFound"})
    with pytest.raises(NotFoundError):
        await aapi.clans.get("000")


async def test_search(aapi, router):
    router.get("/clans").respond(json={"items": [CLAN_JSON]})
    page = await aapi.clans.search(name="wars", limit=5)
    assert page[0].clan_score == 48203


async def test_members_pagination(aapi, router):
    route = router.get("/clans/%232PP/members").mock(
        side_effect=[
            httpx.Response(
                200,
                json={
                    "items": [MEMBER_JSON],
                    "paging": {"cursors": {"after": "C1"}},
                },
            ),
            httpx.Response(200, json={"items": [MEMBER_JSON]}),
        ]
    )
    page = await aapi.clans.members("2PP")
    seen = 0
    async for member in page.iter_all():
        assert member.name == "Andy"
        seen += 1
    assert seen == 2
    assert route.call_count == 2


async def test_player(aapi, router):
    router.get("/players/%23LPP289").respond(json={"tag": "#LPP289", "name": "Andy"})
    player = await aapi.players.get("#LPP289")
    assert player.name == "Andy"


async def test_battle_log(aapi, router):
    router.get("/players/%23LPP289/battlelog").respond(
        json=[{"type": "PVP", "team": [{"crowns": 2}], "opponent": [{"crowns": 1}]}]
    )
    battles = await aapi.players.battle_log("#LPP289")
    assert battles[0].crowns_for == 2


async def test_cards(aapi, router):
    router.get("/cards").respond(json={"items": [{"id": 26000000, "name": {"en": "Knight"}}]})
    page = await aapi.cards.list()
    assert page[0].name.en == "Knight"


async def test_locations_rankings(aapi, router):
    router.get("/locations/57000000/rankings/clans").respond(
        json={"items": [{"tag": "#2PP", "name": "Wars R Us", "rank": 1}]}
    )
    page = await aapi.locations.clan_rankings(57000000)
    assert page[0].rank == 1


async def test_leaderboards(aapi, router):
    router.get("/leaderboards").respond(json=[{"id": 1, "name": {"en": "Ladder"}}])
    boards = await aapi.leaderboards.list()
    assert boards[0].name.en == "Ladder"


async def test_global_tournaments(aapi, router):
    router.get("/globaltournaments").respond(json=[{"tag": "#28QCGU", "maxLosses": 3}])
    tournaments = await aapi.global_tournaments.list()
    assert tournaments[0].max_losses == 3


async def test_tournament_by_tag(aapi, router):
    router.get("/tournaments/%2328QCGU").respond(
        json={"tag": "#28QCGU", "name": "Global", "status": "inProgress"}
    )
    tournament = await aapi.tournaments.get("#28QCGU")
    assert tournament.status == "inProgress"


async def test_clan_war_endpoints(aapi, router):
    router.get("/clans/%232PP/warlog").respond(json={"items": []})
    router.get("/clans/%232PP/currentwar").respond(json={"state": "NOT_IN_WAR"})
    router.get("/clans/%232PP/riverracelog").respond(json={"items": []})
    router.get("/clans/%232PP/currentriverrace").respond(
        json={"state": "ONGOING", "clan": {"tag": "#2PP", "name": "Wars R Us"}}
    )

    assert len(await aapi.clans.war_log("2PP")) == 0
    assert (await aapi.clans.current_war("2PP")).state == "NOT_IN_WAR"
    assert len(await aapi.clans.river_race_log("2PP")) == 0
    assert (await aapi.clans.current_river_race("2PP")).our_clan.name == "Wars R Us"


async def test_cards_all_and_events(aapi, router):
    router.get("/cards").respond(json={"items": [{"id": 26000000, "name": "Knight"}]})
    router.get("/events").respond(json=[{"eventTag": "#EV", "title": "Event"}])

    cards = await aapi.cards.all()
    assert cards[0].name == "Knight"
    events = await aapi.events.list()
    assert events[0].title == "Event"


async def test_leaderboard_endpoints(aapi, router):
    router.get("/leaderboard/1").respond(json={"items": [{"rank": 1, "name": "Andy"}]})
    router.get("/leaderboard/1/leagues/2").respond(json={"items": [{"rank": 2, "name": "Bea"}]})

    assert (await aapi.leaderboards.get(1))[0].rank == 1
    assert (await aapi.leaderboards.league(1, 2))[0].rank == 2


async def test_locations_endpoints(aapi, router):
    router.get("/locations").respond(json={"items": [{"id": 1, "name": "Earth"}]})
    router.get("/locations/1").respond(json={"id": 1, "name": "Earth"})
    router.get("/locations/1/rankings/players").respond(json={"items": []})
    router.get("/locations/1/rankings/clanwars").respond(json={"items": []})
    router.get("/locations/1/pathoflegend/players").respond(json={"items": []})
    router.get("/locations/global/pathoflegend/2022-09/rankings/players").respond(
        json={"items": []}
    )
    router.get("/locations/global/seasons").respond(json=[{"id": "1"}])
    router.get("/locations/global/seasonsV2").respond(json=[{"id": "1"}])
    router.get("/locations/global/seasons/1").respond(json={"id": "1"})
    router.get("/locations/global/seasons/1/rankings/players").respond(json={"items": []})
    router.get("/locations/global/rankings/tournaments/%2328QCGU").respond(json={"items": []})

    assert len(await aapi.locations.list()) == 1
    assert (await aapi.locations.get(1)).name == "Earth"
    assert len(await aapi.locations.player_rankings(1)) == 0
    assert len(await aapi.locations.clan_war_rankings(1)) == 0
    assert len(await aapi.locations.path_of_legend_players(1)) == 0
    assert len(await aapi.locations.path_of_legend_season_rankings("2022-09")) == 0
    assert len(await aapi.locations.league_seasons()) == 1
    assert len(await aapi.locations.league_seasons_v2()) == 1
    assert (await aapi.locations.league_season("1")).id == "1"
    assert len(await aapi.locations.league_season_rankings("1")) == 0
    assert len(await aapi.locations.global_tournament_rankings("#28QCGU")) == 0


async def test_upcoming_chests_and_the_raw_escape_hatch(aapi, router):
    router.get("/players/%23LPP289/upcomingchests").respond(
        json={"items": [{"index": 0, "name": "Silver"}]}
    )
    router.get("/players/%23LPP289").respond(json={"tag": "#LPP289", "name": "Andy"})

    chests = await aapi.players.upcoming_chests("LPP289")
    assert chests[0].name == "Silver"
    assert (await aapi.raw.get("/players/%23LPP289"))["name"] == "Andy"


async def test_tournament_search(aapi, router):
    router.get("/tournaments").respond(json={"items": [{"tag": "#28QCGU", "name": "Global"}]})
    page = await aapi.tournaments.search(name="glo")
    assert page[0].name == "Global"
