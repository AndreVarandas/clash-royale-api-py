"""Pagination helpers.

Endpoints that can return many results come back as a `Page` (or
`AsyncPage`). A page is iterable, so most of the time you never
think about cursors at all::

    for member in api.clans.members("#2PP"):
        print(member.name)

When you *do* want every result across all pages, just say so::

    for member in api.clans.members("#2PP").iter_all():
        print(member.name)
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator, Sequence
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")

FetchSync = Callable[..., "Page[Any]"]
FetchAsync = Callable[..., Awaitable["AsyncPage[Any]"]]


@dataclass(frozen=True)
class Paging:
    """The opaque cursors the API returns with each page."""

    after: str | None = None
    before: str | None = None

    @classmethod
    def from_raw(cls, raw: Any) -> Paging | None:
        """Extract paging from a response body, tolerating both the
        documented ``{"paging": {"cursors": {"after": ...}}}`` shape and flatter ones."""
        if not isinstance(raw, dict):
            return None
        cursors = raw.get("paging") or raw
        if not isinstance(cursors, dict):
            return None
        cursors = cursors.get("cursors") or cursors
        if not isinstance(cursors, dict):
            return None
        paging = cls(after=cursors.get("after"), before=cursors.get("before"))
        if paging.after is None and paging.before is None:
            return None
        return paging


class Page(Sequence[T], Generic[T]):
    """One page of results: iterable, indexable, with paging cursors."""

    def __init__(
        self,
        items: list[T],
        paging: Paging | None = None,
        raw: Any = None,
        fetcher: FetchSync | None = None,
    ) -> None:
        self.items = items
        self._paging = paging
        self._raw = raw
        self._fetcher = fetcher

    @property
    def raw(self) -> Any:
        """The original response body, untouched."""
        return self._raw

    @property
    def cursors(self) -> Paging | None:
        """The paging cursors, if the API sent any."""
        return self._paging

    def next_page(self) -> Page[T] | None:
        """Fetch the page that comes after this one, or ``None`` at the end."""
        if self._fetcher is None or self._paging is None or not self._paging.after:
            return None
        return self._fetcher(after=self._paging.after)

    def iter_all(self) -> Iterator[T]:
        """Yield every item across every remaining page."""
        page: Page[T] | None = self
        while page is not None:
            yield from page.items
            page = page.next_page()

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> T:  # type: ignore[override]
        return self.items[index]

    def __repr__(self) -> str:
        count = len(self.items)
        more = " (+ more pages)" if self._paging and self._paging.after else ""
        return f"<Page with {count} item{'s' if count != 1 else ''}{more}>"


class AsyncPage(Sequence[T], Generic[T]):
    """The async counterpart of ``Page``: same interface, awaited."""

    def __init__(
        self,
        items: list[T],
        paging: Paging | None = None,
        raw: Any = None,
        fetcher: FetchAsync | None = None,
    ) -> None:
        self.items = items
        self._paging = paging
        self._raw = raw
        self._fetcher = fetcher

    @property
    def raw(self) -> Any:
        return self._raw

    @property
    def cursors(self) -> Paging | None:
        return self._paging

    async def next_page(self) -> AsyncPage[T] | None:
        if self._fetcher is None or self._paging is None or not self._paging.after:
            return None
        return await self._fetcher(after=self._paging.after)

    async def iter_all(self) -> AsyncIterator[T]:
        """Async generator yielding every item across every remaining page."""
        page: AsyncPage[T] | None = self
        while page is not None:
            for item in page.items:
                yield item
            page = await page.next_page()

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> T:  # type: ignore[override]
        return self.items[index]

    def __repr__(self) -> str:
        count = len(self.items)
        more = " (+ more pages)" if self._paging and self._paging.after else ""
        return f"<AsyncPage with {count} item{'s' if count != 1 else ''}{more}>"
