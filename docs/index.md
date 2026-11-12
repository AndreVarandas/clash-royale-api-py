# Getting started

An unofficial Python wrapper for the **official Clash Royale API**. It handles
the HTTP calls, authentication, tag encoding, pagination and retries, and
returns typed models for the API's responses.

## Install

```bash
pip install clash-royale-api-py
```

## Get a token

Create a free token at [developer.clashroyale.com/#/account](https://developer.clashroyale.com/#/account).
Each token is bound to specific IP addresses, so make sure your server's IP
is whitelisted — or use a proxy (see below).

## Your first request

```python
from clash_royale_api_py import ClashRoyaleAPI

api = ClashRoyaleAPI("your-token")

clan = api.clans.get("2PP")  # "#2PP", "2pp", " 2PP " — all accepted
print(clan.name, clan.clan_score)
```

!!! tip "No token? No problem."
    Omit the token and the client reads the `CLASH_ROYALE_API_TOKEN`
    (or `CLASH_ROYALE_TOKEN_API`) environment variable — perfect for bots and CI.

## Pagination is just iteration

Endpoints that return many results hand you a `Page`, which is iterable.
One page when you want it, everything when you don't:

```python
page = api.clans.members("2PP")  # one page
for member in page:
    print(member.name)

for member in page.iter_all():  # every remaining page, fetched for you
    print(member.name)
```

## Async, too

```python
from clash_royale_api_py import AsyncClashRoyaleAPI

async with AsyncClashRoyaleAPI("your-token") as api:
    clan = await api.clans.get("2PP")
    members = await api.clans.members("2PP")
    async for member in members.iter_all():
        print(member.name)
```

## Using a proxy

Point the client at the RoyaleAPI proxy if you can't whitelist your IP:

```python
api = ClashRoyaleAPI("your-token", base_url="https://proxy.royaleapi.dev/v1")
```

## The escape hatch

Anything we haven't wrapped is still one call away:

```python
data = api.raw.get("/players/%232PP")
```

## Examples

Runnable scripts live in the
[`examples/`](https://github.com/AndreVarandas/clash-royale-api-py/tree/main/examples)
directory:

- [`clan_report.py`](https://github.com/AndreVarandas/clash-royale-api-py/blob/main/examples/clan_report.py) — members, river race and war log
- [`battle_highlights.py`](https://github.com/AndreVarandas/clash-royale-api-py/blob/main/examples/battle_highlights.py) — battle log
- [`async_demo.py`](https://github.com/AndreVarandas/clash-royale-api-py/blob/main/examples/async_demo.py) — the async client

---

*This content is not affiliated with, endorsed, sponsored, or specifically
approved by Supercell. For more information see
[Supercell's Fan Content Policy](http://www.supercell.com/fan-content-policy).*
