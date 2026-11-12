"""The clan surface: get, search, members, wars — and pagination that reads like Python."""

from __future__ import annotations

import httpx
import pytest

from clash_royale_api_py.exceptions import InvalidTagError, NotFoundError
from tests.conftest import CLAN_JSON, MEMBER_JSON


def test_get_clan_normalizes_the_tag(api, router):
    route = router.get("/clans/%232PP").respond(json=CLAN_JSON)
    clan = api.clans.get(" 2pp ")
    assert clan.name == "Wars R Us"
    assert clan.tag == "#2PP"
    assert clan.clan_score == 48203
    assert route.called
    assert str(route.calls[0].request.headers["Authorization"]) == "Bearer test-token"


def test_get_clan_not_found(api, router):
    router.get("/clans/%23000").respond(
        status_code=404, json={"reason": "notFound", "message": "Clan not found."}
    )
    with pytest.raises(NotFoundError) as excinfo:
        api.clans.get("000")
    assert excinfo.value.status == 404
    assert "Clan not found" in str(excinfo.value)


def test_search_sends_filters_as_camel_case_query_params(api, router):
    route = router.get("/clans").respond(json={"items": [CLAN_JSON]})
    page = api.clans.search(name="wars", min_members=30, min_score=1000, limit=5)
    assert len(page) == 1
    assert page[0].name == "Wars R Us"
    params = route.calls[0].request.url.params
    assert params["name"] == "wars"
    assert params["minMembers"] == "30"
    assert params["minScore"] == "1000"
    assert params["limit"] == "5"


def test_members_page_is_iterable(api, router):
    router.get("/clans/%232PP/members").respond(json={"items": [MEMBER_JSON]})
    page = api.clans.members("#2PP")
    members = list(page)
    assert len(members) == 1
    assert members[0].name == "Andy"
    assert members[0].donations == 100
    assert members[0].donations_received == 90


def test_pagination_walks_the_cursor(api, router):
    route = router.get("/clans/%232PP/members").mock(
        side_effect=[
            httpx.Response(
                200,
                json={
                    "items": [MEMBER_JSON],
                    "paging": {"cursors": {"after": "CURSOR-1"}},
                },
            ),
            httpx.Response(200, json={"items": [MEMBER_JSON]}),
        ]
    )

    page = api.clans.members("#2PP")
    everyone = list(page.iter_all())

    assert len(everyone) == 2
    assert route.call_count == 2
    assert route.calls[1].request.url.params["after"] == "CURSOR-1"


def test_paging_forward_drops_a_stale_before_cursor(api, router):
    route = router.get("/clans/%232PP/members").mock(
        side_effect=[
            httpx.Response(
                200,
                json={
                    "items": [MEMBER_JSON],
                    "paging": {"cursors": {"after": "CURSOR-1"}},
                },
            ),
            httpx.Response(200, json={"items": [MEMBER_JSON]}),
        ]
    )

    page = api.clans.members("#2PP", before="OLD-BEFORE")
    assert page.next_page() is not None

    params = route.calls[1].request.url.params
    assert params["after"] == "CURSOR-1"
    assert "before" not in params


def test_current_war(api, router):
    router.get("/clans/%232PP/currentwar").respond(
        json={"state": "warDay", "clan": {"tag": "#2PP", "name": "Wars R Us", "wins": 1}}
    )
    war = api.clans.current_war("2PP")
    assert war.is_in_war is True
    assert war.clan.name == "Wars R Us"


def test_raw_escape_hatch(api, router):
    route = router.get("/anything/else").respond(json={"ok": True})
    assert api.raw.get("/anything/else") == {"ok": True}
    assert route.called


@pytest.mark.parametrize("tag", ["bad tag!", "###"])
def test_invalid_tags_never_reach_the_api(api, router, tag):
    with pytest.raises(InvalidTagError):
        api.clans.get(tag)
    assert router.calls.call_count == 0
