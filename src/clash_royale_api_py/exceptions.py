"""The exception hierarchy.

Each error carries the HTTP ``status``, the API's ``reason`` and the raw
``body`` so callers can inspect what went wrong without re-parsing responses.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "AuthenticationError",
    "BadRequestError",
    "ClashRoyaleAPIError",
    "GoneError",
    "InvalidTagError",
    "MaintenanceError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "UnknownError",
]


class ClashRoyaleAPIError(Exception):
    """Base class for every error raised by this library.

    Attributes:
        status: The HTTP status code, when the error came from the API.
        reason: The API's machine-readable ``reason``, when present.
        body: The raw response body, when present.
    """

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        reason: str | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.reason = reason
        self.body = body


class InvalidTagError(ValueError, ClashRoyaleAPIError):
    """Raised before any request is made, when a tag cannot be valid.

    Example: ``api.clans.get("hello world!")`` — ``l``, ``w`` and ``!`` are
    not characters that appear in Clash Royale tags, so the library stops
    you right away with a clear explanation instead of a confusing 400.
    """


class BadRequestError(ClashRoyaleAPIError):
    """The API rejected the request (HTTP 400).

    Double-check the parameters you passed — and remember that the library
    normalizes tags for you, so a malformed tag is rarely the culprit here.
    """


class AuthenticationError(ClashRoyaleAPIError):
    """Access was denied (HTTP 403).

    Common causes, in order of likelihood:

    1. The token is wrong or expired — create one at
       developer.clashroyale.com/#/account.
    2. The request is coming from an IP address that is not whitelisted on
       that token. Every token is bound to specific IP addresses; add yours
       (or use a proxy such as https://proxy.royaleapi.dev/v1).
    3. The token does not have access to the requested resource.
    """


class NotFoundError(ClashRoyaleAPIError):
    """The resource does not exist (HTTP 404).

    Check the tag or id you passed — a clan tag like ``#2PP`` must point at
    a clan that still exists. Note that tags are case-insensitive here, so
    ``2pp`` works just as well as ``2PP``.
    """


class GoneError(NotFoundError):
    """The endpoint existed once, but it is gone now (HTTP 410).

    Supercell has permanently removed it — no amount of retrying will help.
    Remove the call from your code. Example: ``currentwar`` was retired when
    classic clan wars were replaced by river races.
    """


class RateLimitError(ClashRoyaleAPIError):
    """You made more requests than your token allows (HTTP 429).

    The library retries these by default. If you see this exception,
    the retries were exhausted — consider adding a small delay between
    requests or spreading the work out.
    """


class MaintenanceError(ClashRoyaleAPIError):
    """The API is temporarily down for maintenance (HTTP 503).

    Nothing is wrong with your code — try again a little later.
    """


class ServerError(ClashRoyaleAPIError):
    """Something went wrong on the API's side (HTTP 5xx).

    The library retries these automatically. If this exception surfaces,
    the API returned an error on every attempt.
    """


class UnknownError(ClashRoyaleAPIError):
    """An error the library could not classify. The ``body`` attribute
    holds the raw response to help you investigate."""
