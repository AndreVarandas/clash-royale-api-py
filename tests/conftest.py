"""Shared fixtures: every test runs offline against mocked transports."""

from __future__ import annotations

import pytest
import respx

from clash_royale_api_py import AsyncClashRoyaleAPI, ClashRoyaleAPI


@pytest.fixture
def router():
    with respx.mock(base_url="https://api.clashroyale.com/v1") as mock:
        yield mock


@pytest.fixture
def api(router):
    client = ClashRoyaleAPI("test-token", retry_backoff=0)
    yield client
    client.close()


@pytest.fixture
async def aapi(router):
    client = AsyncClashRoyaleAPI("test-token", retry_backoff=0)
    yield client
    await client.aclose()


# Tags below only use characters from the real tag alphabet (0289PYLQGRJCUV).
CLAN_JSON = {
    "tag": "#2PP",
    "name": "Wars R Us",
    "description": "We love wars.",
    "type": "inviteOnly",
    "clanScore": 48203,
    "clanWarTrophies": 11403,
    "requiredTrophies": 5000,
    "donationsPerWeek": 1234,
    "members": 47,
    "badgeUrls": {"small": "https://api-assets.clashroyale.com/badges/small.png"},
}

MEMBER_JSON = {
    "tag": "#LPP289",
    "name": "Andy",
    "role": "member",
    "expLevel": 58,
    "trophies": 6102,
    "clanRank": 1,
    "previousClanRank": 2,
    "donations": 100,
    "donationsReceived": 90,
}
