"""Model behavior: reprs, the raw view, containers and helper properties."""

from __future__ import annotations

from clash_royale_api_py.models import (
    Arena,
    Card,
    CardList,
    Chest,
    Clan,
    ClanMember,
    CurrentRiverRace,
    GameMode,
    JsonLocalizedName,
    Leaderboard,
    Location,
    Player,
    RiverRaceClan,
    Tournament,
    UpcomingChests,
)


def test_raw_returns_the_api_camel_case_shape():
    clan = Clan(tag="#2PP", name="Wars R Us", clan_score=48203)
    assert clan.raw["tag"] == "#2PP"
    assert clan.raw["clanScore"] == 48203
    assert clan.raw["name"] == "Wars R Us"


def test_base_repr_falls_back_to_the_class_name():
    assert repr(GameMode()) == "<GameMode>"


def test_base_repr_shows_name_and_tag():
    clan = RiverRaceClan(tag="#2PP", name="Wars R Us")
    assert repr(clan) == "<RiverRaceClan 'Wars R Us' tag='#2PP'>"
    assert str(clan) == repr(clan)


def test_model_specific_reprs():
    assert repr(Card(id=26000000, name="Knight")) == "<Card 'Knight' id=26000000>"
    assert repr(ClanMember(name="Andy", trophies=6102)) == "<ClanMember 'Andy' 6102 trophies>"
    assert repr(Clan(name="Wars R Us", tag="#2PP", members=47)) == (
        "<Clan 'Wars R Us' tag='#2PP' members=47>"
    )
    assert repr(Leaderboard(id=1, name="Ladder")) == "<Leaderboard id=1 'Ladder'>"
    assert repr(Player(name="Andy", tag="#LPP289", trophies=6102)) == (
        "<Player 'Andy' tag='#LPP289' 6102 trophies>"
    )
    assert repr(Tournament(name="Global", tag="#28QCGU", status="inProgress")) == (
        "<Tournament 'Global' tag='#28QCGU' status='inProgress'>"
    )
    assert repr(Arena(id=54000000, name="Legendary Arena")) == (
        "<Arena id=54000000 'Legendary Arena'>"
    )
    assert repr(Location(id=57000000, name="Europe")) == "<Location id=57000000 'Europe'>"


def test_card_list_is_iterable():
    cards = CardList(items=[Card(id=1), Card(id=2)])
    assert len(cards) == 2
    assert [card.id for card in cards] == [1, 2]
    assert cards[1].id == 2


def test_upcoming_chests_is_iterable():
    chests = UpcomingChests(items=[Chest(index=0, name="Silver"), Chest(index=1, name="Gold")])
    assert len(chests) == 2
    assert [chest.index for chest in chests] == [0, 1]
    assert chests[0].name == "Silver"


def test_river_race_points_prefers_the_live_score():
    assert RiverRaceClan(period_points=120, fame=0).points == 120
    assert RiverRaceClan(fame=80).points == 80
    assert RiverRaceClan().points == 0


def test_current_river_race_exposes_the_requested_clan():
    race = CurrentRiverRace(clan=RiverRaceClan(tag="#2PP", name="Wars R Us"))
    assert race.our_clan is race.clan


def test_localized_name_stringifies_and_compares_to_text():
    name = JsonLocalizedName(en="Knight")
    assert str(name) == "Knight"
    assert name == "Knight"
    assert name != 5


def test_localized_name_without_translations_is_empty():
    assert str(JsonLocalizedName()) == ""
