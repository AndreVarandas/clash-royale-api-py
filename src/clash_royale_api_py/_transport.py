"""HTTP plumbing shared by the sync and async clients.

You will rarely need to look at this file. It makes sure every request is
authenticated and every tag is URL-encoded, retries transient failures
(429 / 5xx), and maps HTTP errors to the exceptions in `exceptions`.
"""

from __future__ import annotations

import asyncio
import random
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import httpx

from . import exceptions as exc

DEFAULT_BASE_URL = "https://api.clashroyale.com/v1"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRY_DELAY = 60.0

# HTTP status → exception class.
_STATUS_ERRORS = {
    400: exc.BadRequestError,
    403: exc.AuthenticationError,
    404: exc.NotFoundError,
    410: exc.GoneError,
    429: exc.RateLimitError,
    503: exc.MaintenanceError,
}


def error_for_status(status: int, body: Any) -> exc.ClashRoyaleAPIError:
    """Build the most specific exception for an HTTP status."""
    reason = None
    detail = ""
    if isinstance(body, dict):
        reason = body.get("reason")
        detail = body.get("message") or ""

    if status in _STATUS_ERRORS:
        klass = _STATUS_ERRORS[status]
    elif 500 <= status < 600:
        klass = exc.ServerError
    else:
        klass = exc.UnknownError

    hint = _hint_for(klass, detail)
    message = f"{detail or f'The API answered {status}.'}"
    if hint:
        message = f"{message} {hint}"
    return klass(message, status=status, reason=reason, body=body)


def _hint_for(klass: type[exc.ClashRoyaleAPIError], detail: str) -> str:
    """Pick the advice that actually applies to this response."""
    lowered = detail.lower()
    endpoint_is_down = any(
        phrase in lowered
        for phrase in ("temporarily disabled", "permanently removed", "maintenance")
    )
    if endpoint_is_down and klass is exc.NotFoundError:
        # Telling someone to "check the tag" is wrong when the endpoint
        # itself is disabled — the message already says what happened.
        return ""
    return _HINTS.get(klass, "")


_HINTS = {
    exc.BadRequestError: (
        "Check your query parameters and spelling — tags are normalized for "
        "you, so that is rarely the culprit."
    ),
    exc.AuthenticationError: (
        "Check that your token is valid and that this server's IP address is "
        "whitelisted for the token at developer.clashroyale.com/#/account, or "
        "use a proxy such as https://proxy.royaleapi.dev/v1."
    ),
    exc.NotFoundError: ("Check the tag or id you passed — the resource may not exist (yet)."),
    exc.GoneError: (
        "This endpoint was permanently removed by the API — remove the call "
        "from your code (it will never come back)."
    ),
    exc.RateLimitError: (
        "Too many requests: the library already retried for you, so consider "
        "slowing down or spreading the work out."
    ),
    exc.MaintenanceError: (
        "The API is temporarily down for maintenance — try again a little later."
    ),
    exc.ServerError: ("Something went wrong on the API's side; the request was already retried."),
}


def is_retryable(status: int) -> bool:
    """Whether a status is worth another polite attempt."""
    return status == 429 or status >= 500


def backoff_delay(attempt: int, base: float) -> float:
    """Exponential backoff with a little jitter, honouring nothing fancy."""
    return float(base * (2**attempt) + random.uniform(0, 0.25))


def retry_delay(
    retry_after: str | None,
    attempt: int,
    base: float,
    max_delay: float = DEFAULT_MAX_RETRY_DELAY,
) -> float:
    """Seconds to wait before the next attempt.

    ``Retry-After`` is allowed to be either a number of seconds or an
    HTTP-date (RFC 7231); both are honored, then exponential backoff.
    The result is never larger than ``max_delay`` — a server asking for
    an hour-long sleep should not freeze the client for an hour.
    """
    if retry_after is not None:
        try:
            return min(max(float(retry_after), 0.0), max_delay)
        except ValueError:
            try:
                when = parsedate_to_datetime(retry_after)
            except (TypeError, ValueError):
                pass
            else:
                if when is not None:
                    if when.tzinfo is None:
                        when = when.replace(tzinfo=timezone.utc)
                    seconds = (when - datetime.now(timezone.utc)).total_seconds()
                    return min(max(seconds, 0.0), max_delay)
    return min(backoff_delay(attempt, base), max_delay)


class Transport:
    """The synchronous transport."""

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
        self._max_retries = max_retries
        self._retry_backoff = retry_backoff
        self._max_retry_delay = max_retry_delay
        # A caller-provided client stays theirs: its settings win, and we
        # never close it. Without one, we build (and own) a default.
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {token or ''}",
                "Accept": "application/json",
            },
        )

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET *path* and return the parsed JSON body, retrying transient failures."""
        response = self._send(path, params)
        return response.json()

    def _send(self, path: str, params: dict[str, Any] | None) -> httpx.Response:
        attempt = 0
        while True:
            response = self._client.get(path, params=params)
            if response.status_code >= 400:
                try:
                    body = response.json()
                except ValueError:
                    body = response.text
                if attempt < self._max_retries and is_retryable(response.status_code):
                    delay = retry_delay(
                        response.headers.get("Retry-After"),
                        attempt,
                        self._retry_backoff,
                        self._max_retry_delay,
                    )
                    time.sleep(delay)
                    attempt += 1
                    continue
                raise error_for_status(response.status_code, body)
            return response

    def close(self) -> None:
        """Close the HTTP client — but only one we built ourselves."""
        if self._owns_client:
            self._client.close()


class AsyncTransport:
    """The asynchronous transport."""

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
        self._max_retries = max_retries
        self._retry_backoff = retry_backoff
        self._max_retry_delay = max_retry_delay
        # A caller-provided client stays theirs: its settings win, and we
        # never close it. Without one, we build (and own) a default.
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {token or ''}",
                "Accept": "application/json",
            },
        )

    async def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = await self._send(path, params)
        return response.json()

    async def _send(self, path: str, params: dict[str, Any] | None) -> httpx.Response:
        attempt = 0
        while True:
            response = await self._client.get(path, params=params)
            if response.status_code >= 400:
                try:
                    body = response.json()
                except ValueError:
                    body = response.text
                if attempt < self._max_retries and is_retryable(response.status_code):
                    delay = retry_delay(
                        response.headers.get("Retry-After"),
                        attempt,
                        self._retry_backoff,
                        self._max_retry_delay,
                    )
                    await asyncio.sleep(delay)
                    attempt += 1
                    continue
                raise error_for_status(response.status_code, body)
            return response

    async def close(self) -> None:
        """Close the HTTP client — but only one we built ourselves."""
        if self._owns_client:
            await self._client.aclose()
