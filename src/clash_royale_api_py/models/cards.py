"""Card models."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from ._base import ClashRoyaleModel
from .common import JsonLocalizedName

__all__ = ["Card", "CardList"]


class Card(ClashRoyaleModel):
    """A card in the game: troop, spell, or building."""

    id: int | None = None
    name: str | JsonLocalizedName | None = None
    rarity: str | None = None  # COMMON, RARE, EPIC, LEGENDARY, CHAMPION
    max_level: int | None = None
    elixir_cost: int | None = None
    max_evolution_level: int | None = None
    icon_urls: dict[str, Any] | None = None

    def __repr__(self) -> str:
        return f"<Card {str(self.name or '')!r} id={self.id!r}>"


class CardList(ClashRoyaleModel):
    """Every card in the game, main deck and support cards included."""

    items: list[Card] | None = None
    support_items: list[Card] | None = None

    def __iter__(self) -> Iterator[Card]:  # type: ignore[override]
        return iter(self.items or [])

    def __len__(self) -> int:
        return len(self.items or [])

    def __getitem__(self, index: int) -> Card:
        return (self.items or [])[index]
