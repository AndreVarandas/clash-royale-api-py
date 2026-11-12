"""Players: profiles, chests, and battle logs."""

from __future__ import annotations

from clash_royale_api_py.models import Battle, Player, UpcomingChests

PLAYER_JSON = {
    "tag": "#LPP289",
    "name": "Andy",
    "expLevel": 58,
    "trophies": 6102,
    "bestTrophies": 6400,
    "wins": 1000,
    "losses": 900,
    "battleCount": 1900,
    "threeCrownWins": 300,
    "role": "member",
    "donations": 100,
    "donationsReceived": 90,
    "currentDeck": [{"id": 26000000, "name": {"en": "Knight"}, "level": 14, "maxLevel": 14}],
    "leagueStatistics": {"currentSeason": {"trophies": 6102, "bestTrophies": 6400}},
}


def test_get_player(api, router):
    route = router.get("/players/%23LPP289").respond(json=PLAYER_JSON)
    player = api.players.get("#LPP289")
    assert isinstance(player, Player)
    assert player.name == "Andy"
    assert player.trophies == 6102
    assert player.current_deck[0].name.en == "Knight"
    assert player.current_deck[0].name == "Knight"  # str() feels like the game
    assert route.called


def test_upcoming_chests_are_iterable(api, router):
    router.get("/players/%23LPP289/upcomingchests").respond(
        json={"items": [{"index": 0, "name": {"en": "Magical Chest"}}]}
    )
    chests = api.players.upcoming_chests("#LPP289")
    assert isinstance(chests, UpcomingChests)
    assert len(chests) == 1
    assert chests[0].name == "Magical Chest"


def test_battle_log_returns_battles(api, router):
    router.get("/players/%23LPP289/battlelog").respond(
        json=[
            {
                "type": "PVP",
                "battleTime": "20260101T123456.000Z",
                "team": [{"tag": "#LPP289", "name": "Andy", "crowns": 3, "trophyChange": 29}],
                "opponent": [{"tag": "#YQC089", "name": "Rival", "crowns": 1}],
            }
        ]
    )
    battles = api.players.battle_log("#LPP289")
    assert len(battles) == 1
    battle = battles[0]
    assert isinstance(battle, Battle)
    assert battle.crowns_for == 3
    assert battle.crowns_against == 1
    assert battle.trophy_change == 29
