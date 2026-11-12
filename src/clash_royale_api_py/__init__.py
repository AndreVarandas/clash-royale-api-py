"""clash-royale-api-py — an unofficial Python wrapper for the official Clash Royale API.

Quickstart::

    from clash_royale_api_py import ClashRoyaleAPI

    api = ClashRoyaleAPI("your-token")     # or set CLASH_ROYALE_API_TOKEN

    clan = api.clans.get("2PP")            # "#2PP", "2pp" — all accepted
    print(clan.name, clan.clan_score)

    for member in api.clans.members("2PP").iter_all():
        print(member.name, member.trophies)

Get a free token at https://developer.clashroyale.com/#/account.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .client import AsyncClashRoyaleAPI, ClashRoyaleAPI
from .exceptions import (
    AuthenticationError,
    BadRequestError,
    ClashRoyaleAPIError,
    GoneError,
    InvalidTagError,
    MaintenanceError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UnknownError,
)
from .pagination import AsyncPage, Page, Paging

try:
    __version__ = version("clash-royale-api-py")
except PackageNotFoundError:  # running from a source tree that isn't installed
    __version__ = "0.2.0"

__all__ = [
    "AsyncClashRoyaleAPI",
    "AsyncPage",
    "AuthenticationError",
    "BadRequestError",
    "ClashRoyaleAPI",
    "ClashRoyaleAPIError",
    "GoneError",
    "InvalidTagError",
    "MaintenanceError",
    "NotFoundError",
    "Page",
    "Paging",
    "RateLimitError",
    "ServerError",
    "UnknownError",
    "__version__",
]
