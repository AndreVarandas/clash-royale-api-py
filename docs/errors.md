# Errors

Every failure raises a specific exception, and the message says what to check.
The full hierarchy:

```
ClashRoyaleAPIError
├── InvalidTagError          # also a ValueError; raised before any request
├── BadRequestError          # 400
├── AuthenticationError      # 403 — token invalid/expired, or IP not whitelisted
├── NotFoundError            # 404
│   └── GoneError            # 410 — endpoint permanently removed upstream
├── RateLimitError           # 429 — after retries are exhausted
├── MaintenanceError         # 503
├── ServerError              # 5xx — after retries are exhausted
└── UnknownError             # anything else
```

`GoneError` is a subclass of `NotFoundError`, so `except NotFoundError` catches
both a missing resource (404) and a permanently retired endpoint (410). Catch
`GoneError` first if you need to tell them apart.

`InvalidTagError` is raised before the request is sent, when a tag is empty or
contains characters that never appear in a Clash Royale tag:

```python
from clash_royale_api_py import (
    AuthenticationError,
    ClashRoyaleAPI,
    GoneError,
    InvalidTagError,
    NotFoundError,
    RateLimitError,
)

api = ClashRoyaleAPI()

try:
    clan = api.clans.get("2PP")
except InvalidTagError as error:
    print("That is not a tag:", error)
except AuthenticationError as error:
    print(error)  # token and IP-whitelist guidance
except GoneError as error:
    print("Removed upstream:", error)
except NotFoundError as error:
    print(error.status, error.reason)
except RateLimitError as error:
    print("Retries exhausted:", error)
```

## What every exception carries

`status`, `reason` and `body` are set whenever the error came from the wire, so
you never have to re-parse the response yourself:

```python
except NotFoundError as error:
    print(error.status)   # 404
    print(error.reason)   # the API's machine-readable reason, if any
    print(error.body)     # the raw response body
```

## Retries

Throttled (429) and server (5xx) responses are retried with exponential
backoff and jitter, respecting `Retry-After` when the API sends it.
`GoneError` (410) and `InvalidTagError` are never retried. Configure per client:

```python
api = ClashRoyaleAPI(
    token,
    max_retries=5,  # 3 by default; 0 disables retries
    retry_backoff=1.0,  # base delay in seconds, 0.5 by default
    max_retry_delay=30.0,  # cap for any single wait, 60s by default
)
```

See [Configuration](configuration.md) for the rest of the client options.
