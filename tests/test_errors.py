"""Error mapping and retry behavior."""

from __future__ import annotations

import httpx
import pytest

from clash_royale_api_py import AsyncClashRoyaleAPI, ClashRoyaleAPI
from clash_royale_api_py._transport import retry_delay
from clash_royale_api_py.exceptions import (
    AuthenticationError,
    GoneError,
    MaintenanceError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UnknownError,
)


def test_403_has_actionable_message(router):
    router.get("/clans/%232PP").respond(
        status_code=403, json={"reason": "accessDenied", "message": "Invalid authorization"}
    )
    client = ClashRoyaleAPI("test-token")
    try:
        with pytest.raises(AuthenticationError) as excinfo:
            client.clans.get("2PP")
        assert "developer.clashroyale.com" in str(excinfo.value)
        assert excinfo.value.reason == "accessDenied"
    finally:
        client.close()


def test_410_means_the_endpoint_is_gone_for_good(router):
    router.get("/clans/%232PP/currentwar").respond(
        status_code=410,
        json={"reason": "gone", "message": "This API endpoint has been permanently removed."},
    )
    client = ClashRoyaleAPI("test-token", max_retries=0)
    try:
        with pytest.raises(GoneError) as excinfo:
            client.clans.current_war("2PP")
        error = excinfo.value
        assert error.status == 410
        assert "permanently removed" in str(error)
        # never retried — gone is gone
        assert router.calls.call_count == 1
    finally:
        client.close()


def test_rate_limit_is_retried_and_then_succeeds(router):
    route = router.get("/clans/%232PP").mock(
        side_effect=[
            httpx.Response(429),
            httpx.Response(429),
            httpx.Response(200, json={"tag": "#2PP", "name": "Wars R Us"}),
        ]
    )
    client = ClashRoyaleAPI("test-token", retry_backoff=0)
    try:
        clan = client.clans.get("2PP")
        assert clan.name == "Wars R Us"
        assert route.call_count == 3
    finally:
        client.close()


def test_rate_limit_exhausted_raises(router):
    router.get("/clans/%232PP").respond(status_code=429, json={"reason": "throttled"})
    client = ClashRoyaleAPI("test-token", max_retries=1, retry_backoff=0)
    try:
        with pytest.raises(RateLimitError):
            client.clans.get("2PP")
        assert router.calls.call_count == 2
    finally:
        client.close()


def test_maintenance_raises_after_retries(router):
    router.get("/clans/%232PP").respond(status_code=503)
    client = ClashRoyaleAPI("test-token", max_retries=1, retry_backoff=0)
    try:
        with pytest.raises(MaintenanceError):
            client.clans.get("2PP")
    finally:
        client.close()


def test_server_error_is_retryable(router):
    router.get("/clans/%232PP").mock(
        side_effect=[
            httpx.Response(500),
            httpx.Response(200, json={"tag": "#2PP", "name": "Wars R Us"}),
        ]
    )
    client = ClashRoyaleAPI("test-token", retry_backoff=0)
    try:
        assert client.clans.get("2PP").name == "Wars R Us"
    finally:
        client.close()


def test_unparseable_error_body_still_raises(router):
    router.get("/clans/%232PP").respond(status_code=500, text="oops")
    client = ClashRoyaleAPI("test-token", max_retries=0)
    try:
        with pytest.raises(ServerError):
            client.clans.get("2PP")
    finally:
        client.close()


def test_unknown_status_maps_to_unknown_error(router):
    router.get("/clans/%232PP").respond(status_code=418, json={"message": "I am a teapot."})
    client = ClashRoyaleAPI("test-token", max_retries=0)
    try:
        with pytest.raises(UnknownError) as excinfo:
            client.clans.get("2PP")
        assert excinfo.value.status == 418
        assert "teapot" in str(excinfo.value)
    finally:
        client.close()


def test_token_from_environment(router, monkeypatch):
    monkeypatch.setenv("CLASH_ROYALE_API_TOKEN", "env-token")
    route = router.get("/clans/%232PP").respond(json={"tag": "#2PP"})
    client = ClashRoyaleAPI()
    try:
        client.clans.get("2PP")
        assert str(route.calls[0].request.headers["Authorization"]) == "Bearer env-token"
    finally:
        client.close()


def test_token_from_the_other_common_environment_name(router, monkeypatch):
    monkeypatch.delenv("CLASH_ROYALE_API_TOKEN", raising=False)
    monkeypatch.setenv("CLASH_ROYALE_TOKEN_API", "npm-style-token")
    route = router.get("/clans/%232PP").respond(json={"tag": "#2PP"})
    client = ClashRoyaleAPI()
    try:
        client.clans.get("2PP")
        assert str(route.calls[0].request.headers["Authorization"]) == "Bearer npm-style-token"
    finally:
        client.close()


def test_missing_token_fails_fast_with_guidance(monkeypatch):
    monkeypatch.delenv("CLASH_ROYALE_API_TOKEN", raising=False)
    monkeypatch.delenv("CLASH_ROYALE_TOKEN_API", raising=False)
    with pytest.raises(AuthenticationError) as excinfo:
        ClashRoyaleAPI()
    assert "CLASH_ROYALE_API_TOKEN" in str(excinfo.value)


def test_disabled_endpoint_does_not_blame_your_tag(router):
    router.get("/clans/%232PP/warlog").respond(
        status_code=404,
        json={
            "reason": "notFound",
            "message": "This API endpoint has been temporarily disabled, "
            "possibilities to bring it back are being investigated.",
        },
    )
    client = ClashRoyaleAPI("test-token", max_retries=0)
    try:
        with pytest.raises(NotFoundError) as excinfo:
            client.clans.war_log("2PP")
        message = str(excinfo.value)
        assert "temporarily disabled" in message
        assert "Check the tag" not in message
    finally:
        client.close()


def test_retry_after_accepts_seconds():
    assert retry_delay("2", 0, 0.5) == 2.0


def test_retry_after_accepts_an_http_date():
    # A date in the past means "retry now".
    assert retry_delay("Wed, 21 Oct 2015 07:28:00 GMT", 0, 0.5) == 0.0


def test_retry_after_accepts_a_naive_http_date():
    # No timezone in the header: treat it as UTC rather than crashing.
    assert retry_delay("Wed, 21 Oct 2015 07:28:00", 0, 0.5) == 0.0


def test_retry_after_falls_back_to_backoff_when_unparseable():
    assert retry_delay("soon-ish", 1, 0.5) >= 1.0


def test_retry_after_is_capped_so_a_rude_header_cannot_freeze_us():
    # The default cap is 60 seconds, even if the server asks for an hour.
    assert retry_delay("3600", 0, 0.5) == 60.0
    assert retry_delay("3600", 0, 0.5, max_delay=5.0) == 5.0


def test_backoff_is_capped_too():
    assert retry_delay(None, 20, 0.5, max_delay=10.0) <= 10.0


async def test_async_rate_limit_is_retried(router):
    route = router.get("/clans/%232PP").mock(
        side_effect=[
            httpx.Response(429),
            httpx.Response(200, json={"tag": "#2PP", "name": "Wars R Us"}),
        ]
    )
    client = AsyncClashRoyaleAPI("test-token", retry_backoff=0)
    try:
        clan = await client.clans.get("2PP")
        assert clan.name == "Wars R Us"
        assert route.call_count == 2
    finally:
        await client.aclose()


def test_custom_http_client_needs_no_token_and_is_never_closed(router, monkeypatch):
    monkeypatch.delenv("CLASH_ROYALE_API_TOKEN", raising=False)
    monkeypatch.delenv("CLASH_ROYALE_TOKEN_API", raising=False)
    route = router.get("/clans/%232PP").respond(json={"tag": "#2PP", "name": "Wars R Us"})

    http_client = httpx.Client(
        base_url="https://api.clashroyale.com/v1",
        headers={"Authorization": "Bearer custom-token"},
    )
    api = ClashRoyaleAPI(http_client=http_client)
    try:
        with api:  # exiting the context manager must not close someone else's client
            assert api.clans.get("2PP").name == "Wars R Us"
        assert not http_client.is_closed
        assert str(route.calls[0].request.headers["Authorization"]) == "Bearer custom-token"
    finally:
        http_client.close()
