"""Client wiring: exposed version and lifecycle/context-manager behavior."""

from __future__ import annotations

import importlib
import importlib.metadata
from importlib.metadata import version

import clash_royale_api_py
from clash_royale_api_py import (
    AsyncClashRoyaleAPI,
    ClashRoyaleAPI,
    __version__,
)


def test_version_is_exposed_and_matches_the_installed_distribution():
    assert __version__ == version("clash-royale-api-py")
    assert __version__ != "0.0.0"


def test_version_falls_back_when_the_distribution_is_not_installed(monkeypatch):
    def not_installed(name):
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", not_installed)
    try:
        reloaded = importlib.reload(clash_royale_api_py)
        assert reloaded.__version__ == "0.0.0"
    finally:
        monkeypatch.undo()
        importlib.reload(clash_royale_api_py)


def test_sync_context_manager_returns_the_client_and_closes_it():
    api = ClashRoyaleAPI("test-token")
    with api as entered:
        assert entered is api
        assert not api._transport._client.is_closed
    assert api._transport._client.is_closed


async def test_async_context_manager_returns_the_client_and_closes_it():
    api = AsyncClashRoyaleAPI("test-token")
    async with api as entered:
        assert entered is api
        assert not api._transport._client.is_closed
    assert api._transport._client.is_closed
