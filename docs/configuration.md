# Configuration

Both clients take the same options. The only difference is `http_client`'s
type and how you close the client.

## Token

Pass it directly, or let it come from the environment:

```python
from clash_royale_api_py import ClashRoyaleAPI

api = ClashRoyaleAPI("your-token")
```

```python
import os

os.environ["CLASH_ROYALE_API_TOKEN"] = "your-token"

api = ClashRoyaleAPI()  # reads the env var
```

Accepted variables, in order: `CLASH_ROYALE_API_TOKEN`, then
`CLASH_ROYALE_TOKEN_API`. Get a free token at
<https://developer.clashroyale.com/#/account>. If no token is found and you did
not supply `http_client`, construction raises `AuthenticationError`.

## Everything at once

```python
api = ClashRoyaleAPI(
    "your-token",
    base_url="https://api.clashroyale.com/v1",
    timeout=30.0,
    max_retries=3,
    retry_backoff=0.5,
    max_retry_delay=60.0,
    http_client=None,
)
```

| Option | Default | Meaning |
|---|---|---|
| `token` | `None` | API token; falls back to the environment variables above |
| `base_url` | `https://api.clashroyale.com/v1` | API root — point it at a proxy if needed |
| `timeout` | `30.0` | Request timeout in seconds |
| `max_retries` | `3` | Retries for 429 / 5xx; `0` disables retries |
| `retry_backoff` | `0.5` | Base delay in seconds for exponential backoff |
| `max_retry_delay` | `60.0` | Upper bound for any single wait, including `Retry-After` |
| `http_client` | `None` | Your own `httpx.Client` / `httpx.AsyncClient` |

## Proxy

The official API only accepts requests from IPs whitelisted on your token. If
your server can't hold a stable IP, point the client at the RoyaleAPI proxy:

```python
api = ClashRoyaleAPI(
    "your-token",
    base_url="https://proxy.royaleapi.dev/v1",
)
```

## Bring your own HTTP client

Useful when you already have a configured `httpx.Client` — custom transport,
logging hooks, an auth header, or a mock in tests:

```python
import httpx

with httpx.Client(
    base_url="https://proxy.royaleapi.dev/v1",
    headers={"Authorization": "Bearer your-token"},
) as http:
    api = ClashRoyaleAPI(http_client=http)
```

Your client's base URL and headers win over the arguments above, and the token
may be omitted entirely. The library never closes a client you passed in — it
stays yours.

## Closing

```python
api = ClashRoyaleAPI("your-token")
try:
    clan = api.clans.get("2PP")
finally:
    api.close()
```

The clients are context managers, which is usually tidier:

```python
with ClashRoyaleAPI("your-token") as api:
    clan = api.clans.get("2PP")
```

```python
async with AsyncClashRoyaleAPI("your-token") as api:
    clan = await api.clans.get("2PP")
```

For async code outside a `with` block, call `await api.aclose()`.
