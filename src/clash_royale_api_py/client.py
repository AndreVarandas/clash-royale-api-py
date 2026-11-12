"""The two clients: `ClashRoyaleAPI` (sync) and `AsyncClashRoyaleAPI`.

This is the whole public entry point::

    from clash_royale_api_py import ClashRoyaleAPI

    api = ClashRoyaleAPI("your-token")
    clan = api.clans.get("2PP")
"""

from __future__ import annotations

import os
from types import TracebackType

import httpx

from ._transport import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    AsyncTransport,
    Transport,
)
from .exceptions import AuthenticationError
from .resources import (
    AsyncCards,
    AsyncClans,
    AsyncEvents,
    AsyncGlobalTournaments,
    AsyncLeaderboards,
    AsyncLocations,
    AsyncPlayers,
    AsyncRaw,
    AsyncTournaments,
    Cards,
    Clans,
    Events,
    GlobalTournaments,
    Leaderboards,
    Locations,
    Players,
    Raw,
    Tournaments,
)

__all__ = ["AsyncClashRoyaleAPI", "ClashRoyaleAPI"]

# Both spellings are common in the wild — accept either one.
TOKEN_ENV_VARS = ("CLASH_ROYALE_API_TOKEN", "CLASH_ROYALE_TOKEN_API")


def _resolve_token(token: str | None) -> str:
    resolved = token or next(
        (os.environ[name] for name in TOKEN_ENV_VARS if os.environ.get(name)), None
    )
    if not resolved:
        raise AuthenticationError(
            "No API token was provided. Pass one to the client, or set the "
            f"{TOKEN_ENV_VARS[0]} (or {TOKEN_ENV_VARS[1]}) environment variable. "
            "Get a token (it's free) at https://developer.clashroyale.com/#/account."
        )
    return resolved


class ClashRoyaleAPI:
    """Entry point to the official Clash Royale API.

    Example::

        api = ClashRoyaleAPI("your-token")

        clan = api.clans.get("2PP")            # tags are normalized for you
        print(clan.name, clan.clan_score)

        for member in api.clans.members("2PP"):
            print(member.name, member.trophies)
    """

    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        retry_backoff: float = 0.5,
        max_retry_delay: float = DEFAULT_MAX_RETRY_DELAY,
        http_client: httpx.Client | None = None,
    ) -> None:
        """Create the client.

        Args:
            token: Your API token from developer.clashroyale.com. If omitted,
                the ``CLASH_ROYALE_API_TOKEN`` (or ``CLASH_ROYALE_TOKEN_API``)
                environment variable is used. Not needed at all when you bring
                your own ``http_client`` that already authenticates.
            base_url: API root. Point this at a proxy such as
                ``https://proxy.royaleapi.dev/v1`` if you can't whitelist
                your server's IP on the token.
            timeout: Request timeout in seconds.
            max_retries: How many times to retry throttled (429) or
                failing (5xx) requests before raising.
            retry_backoff: Base delay in seconds for the exponential backoff.
            max_retry_delay: Upper bound (seconds) for any single retry wait,
                including one asked for by a ``Retry-After`` header.
            http_client: Bring your own ``httpx.Client`` if you like. Its base
                URL and headers win, the ``token`` argument may be omitted,
                and the library never closes it — it stays yours.
        """
        self._transport = Transport(
            token if http_client is not None else _resolve_token(token),
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            max_retry_delay=max_retry_delay,
            http_client=http_client,
        )
        self.clans = Clans(self._transport)
        self.players = Players(self._transport)
        self.cards = Cards(self._transport)
        self.events = Events(self._transport)
        self.tournaments = Tournaments(self._transport)
        self.global_tournaments = GlobalTournaments(self._transport)
        self.locations = Locations(self._transport)
        self.leaderboards = Leaderboards(self._transport)
        self.raw = Raw(self._transport)

    def close(self) -> None:
        """Release the underlying connections."""
        self._transport.close()

    def __enter__(self) -> ClashRoyaleAPI:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


class AsyncClashRoyaleAPI:
    """Async counterpart of `ClashRoyaleAPI`: same methods, awaited.

    Example::

        async with AsyncClashRoyaleAPI("your-token") as api:
            clan = await api.clans.get("2PP")
            print(clan.name)

            members = await api.clans.members("2PP")
            async for member in members.iter_all():
                print(member.name)
    """

    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        retry_backoff: float = 0.5,
        max_retry_delay: float = DEFAULT_MAX_RETRY_DELAY,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """See `ClashRoyaleAPI` for the meaning of each argument."""
        self._transport = AsyncTransport(
            token if http_client is not None else _resolve_token(token),
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            max_retry_delay=max_retry_delay,
            http_client=http_client,
        )
        self.clans = AsyncClans(self._transport)
        self.players = AsyncPlayers(self._transport)
        self.cards = AsyncCards(self._transport)
        self.events = AsyncEvents(self._transport)
        self.tournaments = AsyncTournaments(self._transport)
        self.global_tournaments = AsyncGlobalTournaments(self._transport)
        self.locations = AsyncLocations(self._transport)
        self.leaderboards = AsyncLeaderboards(self._transport)
        self.raw = AsyncRaw(self._transport)

    async def aclose(self) -> None:
        await self._transport.close()

    async def __aenter__(self) -> AsyncClashRoyaleAPI:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()
