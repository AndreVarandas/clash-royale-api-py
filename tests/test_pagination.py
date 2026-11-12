"""Page / AsyncPage behavior, cursor parsing and their fallbacks."""

from __future__ import annotations

import pytest

from clash_royale_api_py.pagination import AsyncPage, Page, Paging


def test_paging_accepts_the_nested_documented_shape():
    assert Paging.from_raw({"paging": {"cursors": {"after": "A"}}}) == Paging(after="A")


def test_paging_accepts_flatter_shapes():
    assert Paging.from_raw({"cursors": {"before": "B"}}) == Paging(before="B")
    assert Paging.from_raw({"after": "A", "before": "B"}) == Paging(after="A", before="B")


@pytest.mark.parametrize(
    "raw",
    [
        None,
        [],
        "not-a-body",
        {},
        {"after": None},
        {"paging": "not-a-dict"},
        {"paging": {"cursors": "not-a-dict"}},
    ],
)
def test_paging_returns_none_when_there_is_nothing_usable(raw):
    assert Paging.from_raw(raw) is None


def test_page_behaves_like_a_sequence_and_exposes_its_raw_body():
    page = Page([1, 2], paging=Paging(after="A"), raw={"items": [1, 2]})
    assert list(page) == [1, 2]
    assert len(page) == 2
    assert page[0] == 1
    assert page.raw == {"items": [1, 2]}
    assert page.cursors == Paging(after="A")


def test_page_repr_reports_items_and_remaining_pages():
    assert repr(Page([1])) == "<Page with 1 item>"
    assert repr(Page([1, 2], Paging(after="A"))) == "<Page with 2 items (+ more pages)>"


def test_page_walks_forward_with_its_fetcher():
    def fetcher(after):
        return Page([3])

    page = Page([1, 2], paging=Paging(after="A"), fetcher=fetcher)
    assert list(page.iter_all()) == [1, 2, 3]
    assert page.next_page().items == [3]
    assert Page([1]).next_page() is None


async def test_async_page_behaves_like_a_sequence_and_exposes_its_raw_body():
    page = AsyncPage([1, 2], paging=Paging(after="A"), raw={"items": [1, 2]})
    assert list(page) == [1, 2]
    assert len(page) == 2
    assert page[1] == 2
    assert page.raw == {"items": [1, 2]}
    assert page.cursors == Paging(after="A")
    assert repr(page) == "<AsyncPage with 2 items (+ more pages)>"
    assert repr(AsyncPage([1])) == "<AsyncPage with 1 item>"


async def test_async_page_walks_forward_with_its_fetcher():
    async def fetcher(after):
        return AsyncPage([3])

    page = AsyncPage([1, 2], paging=Paging(after="A"), fetcher=fetcher)
    assert [item async for item in page.iter_all()] == [1, 2, 3]
    assert (await page.next_page()).items == [3]
    assert await AsyncPage([1]).next_page() is None
