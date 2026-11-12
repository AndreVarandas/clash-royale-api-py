"""Small models shared across the whole API."""

from __future__ import annotations

from ._base import ClashRoyaleModel


class JsonLocalizedName(ClashRoyaleModel):
    """A name localized into several languages.

    Access languages as attributes (``name.en``) or just ``str()`` the whole
    thing to get the first available translation.
    """

    def __str__(self) -> str:
        dump = self.model_dump()
        for value in dump.values():
            if isinstance(value, str) and value:
                return value
        return ""

    def __eq__(self, other: object) -> bool:
        # ``card.name == "Knight"`` should read as beautifully as it behaves.
        if isinstance(other, str):
            return str(self) == other
        return super().__eq__(other)


class BadgeUrls(ClashRoyaleModel):
    """URLs for a clan badge image, keyed by size (``small``, ``medium``...)."""


class IconUrls(ClashRoyaleModel):
    """URLs for an icon image, keyed by size."""


class Arena(ClashRoyaleModel):
    """The arena a player or clan is currently in.

    ``name`` comes back as a plain string from the API (the API docs claim a
    localized object — reality wins). ``str(arena.name)`` always gives text.
    """

    id: int | None = None
    name: str | JsonLocalizedName | None = None
    raw_name: str | None = None
    icon_urls: IconUrls | None = None

    def __repr__(self) -> str:
        return f"<Arena id={self.id!r} {str(self.name or '')!r}>"


class GameMode(ClashRoyaleModel):
    """A game mode (ladder, 2v2, river race...)."""

    id: int | None = None
    name: str | None = None


class Location(ClashRoyaleModel):
    """A location: a country or a region used for local leaderboards."""

    id: int | None = None
    name: str | None = None
    is_country: bool | None = None
    country_code: str | None = None
    localized_name: JsonLocalizedName | None = None

    def __repr__(self) -> str:
        return f"<Location id={self.id!r} {self.name!r}>"


class LeagueSeason(ClashRoyaleModel):
    """A Path of Legend / league season, identified by its ``id``.

    ``seasonsV2`` additionally carries ``unique_id``, ``end_time`` and
    ``code`` — the older ``seasons`` endpoint only sends ``id``.
    """

    id: str | None = None
    unique_id: str | None = None
    end_time: str | None = None
    code: str | None = None
