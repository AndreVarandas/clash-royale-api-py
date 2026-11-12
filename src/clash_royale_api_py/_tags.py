"""Helpers for normalizing Clash Royale tags.

Players write tags in every shape imaginable — ``2PP``, ``#2PP``, ``%232PP``,
even with stray spaces. This library accepts them all, so nobody ever sees a
400 error just because of a missing ``#``.
"""

from __future__ import annotations

from urllib.parse import quote

from .exceptions import InvalidTagError

# The only characters that can legally appear inside a Clash Royale tag.
TAG_ALPHABET = frozenset("0289PYLQGRJCUV")

_INVALID_TAG_HINT = (
    "A Clash Royale tag looks like #2PP and only uses these characters: "
    "0289PYLQGRJCUV. Check that you copied the whole tag without extra text."
)


def _invalid_tag(tag: str) -> InvalidTagError:
    return InvalidTagError(f"Invalid tag {tag!r}. {_INVALID_TAG_HINT}")


def normalize_tag(tag: str) -> str:
    """Return *tag* cleaned up: no ``#``, no spaces, uppercased.

    Raises:
        InvalidTagError: if the tag is empty or contains characters that
            can never appear in a real tag (a good early hint that the tag
            was copied with extra text or is simply wrong).
    """
    cleaned = tag.strip().replace(" ", "").replace("%23", "#").replace("#", "").upper()
    if not cleaned:
        raise _invalid_tag(tag)
    invalid = set(cleaned) - TAG_ALPHABET
    if invalid:
        raise _invalid_tag(tag)
    return cleaned


def tag_path_segment(tag: str) -> str:
    """Return *tag* normalized, ``#``-prefixed and URL-encoded.

    ``"2PP"`` becomes ``%232PP`` — exactly what the API expects.
    """
    return quote(f"#{normalize_tag(tag)}", safe="")
