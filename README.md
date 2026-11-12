# Clash Royale API — Python

[![PyPI](https://img.shields.io/pypi/v/clash-royale-api-py.svg)](https://pypi.org/project/clash-royale-api-py/)
[![Python](https://img.shields.io/pypi/pyversions/clash-royale-api-py.svg)](https://pypi.org/project/clash-royale-api-py/)
[![CI](https://github.com/AndreVarandas/clash-royale-api-py/actions/workflows/ci.yml/badge.svg)](https://github.com/AndreVarandas/clash-royale-api-py/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/AndreVarandas/clash-royale-api-py/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-online-indigo.svg)](https://andrevarandas.github.io/clash-royale-api-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/AndreVarandas/clash-royale-api-py/blob/main/LICENSE)

An unofficial Python wrapper for the **official Clash Royale API**
(<https://developer.clashroyale.com>).

It handles the HTTP calls, authentication, tag encoding, pagination and
retries, and returns typed models for the API's responses.

This project is not affiliated with, endorsed, or sponsored by Supercell. You
need your own token from the official developer portal.

---

## Getting started

```bash
pip install clash-royale-api-py
```

Grab a free token at [developer.clashroyale.com/#/account](https://developer.clashroyale.com/#/account)
and you're ready.

## Usage

```python
from clash_royale_api_py import ClashRoyaleAPI

api = ClashRoyaleAPI("the-token-you-got-from-the-api")

# Get a clan — "2PP", "#2PP", " 2pp " are all accepted.
clan = api.clans.get("2PP")
print(clan.name, clan.clan_score)

# Rosters, wars and river races; paginated results are iterable.
for member in api.clans.members("2PP").iter_all():
    print(member.name, member.trophies)

race = api.clans.current_river_race("2PP")
if race.clans:
    print("Points:", [(c.name, c.points) for c in race.clans])
```

No token argument? The client reads the `CLASH_ROYALE_API_TOKEN`
(or `CLASH_ROYALE_TOKEN_API`) environment variable:

```python
import os
os.environ["CLASH_ROYALE_API_TOKEN"] = "your-token"

api = ClashRoyaleAPI()          # reads the env var for you
player = api.players.get("#LPP289")
print(player.name, player.trophies, player.arena.name)
```

### Async support

Both clients share one implementation and behave the same way:

```python
import asyncio
from clash_royale_api_py import AsyncClashRoyaleAPI

async def main():
    async with AsyncClashRoyaleAPI("your-token") as api:
        clan = await api.clans.get("2PP")
        print(clan.name)

        entries = await api.leaderboards.get(0)
        async for entry in entries.iter_all():
            print(entry.rank, entry.name)

asyncio.run(main())
```

### Resources

| Client attribute | Available methods |
|---|---|
| `api.clans` | `search`, `get`, `members`, `war_log`, `current_war` (retired upstream — raises `GoneError`), `river_race_log`, `current_river_race` |
| `api.players` | `get`, `upcoming_chests`, `battle_log` |
| `api.cards` | `list`, `all` |
| `api.events` | `list` |
| `api.tournaments` | `search`, `get` |
| `api.global_tournaments` | `list` |
| `api.locations` | `list`, `get`, `clan_rankings`, `clan_war_rankings`, `player_rankings`, `path_of_legend_players`, `path_of_legend_season_rankings`, `league_seasons`, `league_seasons_v2`, `league_season`, `league_season_rankings`, `global_tournament_rankings` |
| `api.leaderboards` | `list`, `get`, `league` |
| `api.raw` | Escape hatch: `api.raw.get("/players/%23ABC")` for endpoints that aren't wrapped |

Methods that return a `Page` accept `limit=`, `after=` and `before=`; see the
[Resources docs](https://andrevarandas.github.io/clash-royale-api-py/resources/)
for the full list.

### Errors

Failures raise a specific exception type per HTTP status:

```python
from clash_royale_api_py import AuthenticationError, InvalidTagError, NotFoundError

try:
    clan = api.clans.get("2PP")
except InvalidTagError as e:
    print(e)          # bad tag characters, raised before any request
except AuthenticationError as e:
    print(e)          # invalid token, or the server IP isn't whitelisted
except NotFoundError as e:
    print(e.status)   # 404 (this also catches GoneError, a 410)
```

Throttled (429) and 5xx responses are retried with exponential backoff by
default. Tune it with `max_retries=`, `retry_backoff=` and `max_retry_delay=`,
or pass `max_retries=0` to disable retries.

### Using a proxy

The official API only accepts requests from IPs whitelisted on your token.
If your server can't hold a stable IP, use the RoyaleAPI proxy:

```python
api = ClashRoyaleAPI(
    "your-token",
    base_url="https://proxy.royaleapi.dev/v1",
)
```

The [Configuration docs](https://andrevarandas.github.io/clash-royale-api-py/configuration/)
cover timeouts, retries and bringing your own `httpx` client.

## About the proxy server

The proxy server is a service provided by the RoyaleAPI team. It allows you
to make requests to the official API without whitelisting every IP you use.
If you want to host your own, there's a Nuxt web app for that at
<https://github.com/AndreVarandas/royale-proxy-api>.

## Development

```bash
uv sync            # install everything
uv run pytest      # tests (fully offline, via respx)
uv run ruff check src tests
uv run mypy src
uv run mkdocs serve  # the docs site
```

Runnable scripts live in [`examples/`](https://github.com/AndreVarandas/clash-royale-api-py/tree/main/examples).

## License

MIT — see [LICENSE](https://github.com/AndreVarandas/clash-royale-api-py/blob/main/LICENSE).

---

*This content is not affiliated with, endorsed, sponsored, or specifically
approved by Supercell, and Supercell is not responsible for it. For more
information see [Supercell's Fan Content Policy](http://www.supercell.com/fan-content-policy).*
