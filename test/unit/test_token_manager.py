# pylint: disable=protected-access
import json
import stat
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Optional
from unittest.mock import Mock, call

import pytest
from groundlight import token_manager
from groundlight.token_manager import (
    REFRESH_INTERVAL_FRACTION,
    REFRESH_RETRY_BACKOFF_SECONDS,
    TOKEN_NAME_MAX_LENGTH,
    TokenManager,
    TokenManagerError,
)
from groundlight_openapi_client import Configuration
from groundlight_openapi_client.exceptions import ApiException, NotFoundException, UnauthorizedException

CONFIGURED_TOKEN = "api_configured_token_value_long"
NOW = datetime(2026, 7, 9, 12, 0, tzinfo=timezone.utc)
TOKEN_TTL = timedelta(days=30)
REFRESH_INTERVAL = TOKEN_TTL * REFRESH_INTERVAL_FRACTION
TOKEN_CACHE_MODE = 0o600
TOKEN_DIR_MODE = 0o700
_UNSET = object()


def _expiring_metadata(name: str, raw_key: str) -> SimpleNamespace:
    """Build by-snippet metadata for an expiring configured token."""
    return SimpleNamespace(name=name, raw_key_snippet=raw_key[:20], expires_at=NOW + TOKEN_TTL)


def _never_expire_metadata(name: str, raw_key: str) -> SimpleNamespace:
    """Build by-snippet metadata for a never-expire configured token."""
    return SimpleNamespace(name=name, raw_key_snippet=raw_key[:20], expires_at=None)


def _created_token(
    name: str,
    raw_key: str,
    now: datetime,
    *,
    expires_at=_UNSET,
    created_at: Optional[datetime] = None,
) -> SimpleNamespace:
    """Build a token creation response. Pass expires_at=None for a never-expire child."""
    resolved_created_at = now if created_at is None else created_at
    resolved_expires_at = now + TOKEN_TTL if expires_at is _UNSET else expires_at
    return SimpleNamespace(
        name=name,
        raw_key=raw_key,
        raw_key_snippet=raw_key[:20],
        created_at=resolved_created_at,
        expires_at=resolved_expires_at,
    )


def _manager(mocker, tmp_path, api, now=NOW) -> TokenManager:
    """Create a token manager with deterministic API and time dependencies."""
    mocker.patch.object(token_manager, "ApiTokensApi", return_value=api)
    mocker.patch.object(token_manager, "_utc_now", return_value=now)
    configuration = Configuration(host="https://example.com/device-api")
    configuration.api_key["ApiToken"] = CONFIGURED_TOKEN
    return TokenManager(
        configured_token=CONFIGURED_TOKEN,
        configuration=configuration,
        request_timeout=1,
        token_dir=tmp_path,
    )


def test_initialization_mints_and_privately_caches_token(mocker, tmp_path):
    """An expiring configured token mints a child and stores it with mode 0600."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)

    manager = _manager(mocker, tmp_path, api)

    request = api.create_api_token.call_args.args[0]
    assert request.name.startswith("Device token ")
    assert "expires_at" not in request._data_store  # server-authoritative mint; no client TTL
    assert manager._configuration.api_key["ApiToken"] == "api_working_token_one"
    assert stat.S_IMODE(manager._slot_path.stat().st_mode) == TOKEN_CACHE_MODE
    cached = json.loads(manager._slot_path.read_text())
    assert cached["base_name"] == "Device token"
    assert cached["current"]["raw_key"] == "api_working_token_one"
    assert cached["current"]["ttl_seconds"] == TOKEN_TTL.total_seconds()
    assert cached["previous"]["name"] == "Device token"
    api.delete_api_token.assert_not_called()


def test_initialization_parks_configured_token_as_previous(mocker, tmp_path):
    """After minting the first working token, the configured token is parked as previous."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)

    manager = _manager(mocker, tmp_path, api)

    api.delete_api_token.assert_not_called()
    cached = json.loads(manager._slot_path.read_text())
    assert cached["previous"]["name"] == "Device token"
    assert cached["previous"]["minted_at"] == NOW.isoformat().replace("+00:00", "Z")


def test_initialization_uses_never_expire_configured_token_as_is(mocker, tmp_path):
    """A never-expire configured token is used directly with no mint or refresh thread."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _never_expire_metadata("Device token", CONFIGURED_TOKEN)

    manager = _manager(mocker, tmp_path, api)
    manager.start()

    assert manager._configuration.api_key["ApiToken"] == CONFIGURED_TOKEN
    assert manager._current is None
    assert manager._thread is None
    assert not manager._slot_path.exists()
    api.create_api_token.assert_not_called()


def test_initialization_mint_with_null_expires_at_does_not_start_refresh(mocker, tmp_path):
    """A minted child with null expires_at is activated but does not start a refresh thread."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token(
        "Device token abc123", "api_working_token_one", NOW, expires_at=None
    )

    manager = _manager(mocker, tmp_path, api)
    manager.start()

    assert manager._configuration.api_key["ApiToken"] == "api_working_token_one"
    assert manager._current is not None
    assert manager._current.expires_at is None
    assert manager._thread is None
    cached = json.loads(manager._slot_path.read_text())
    assert cached["current"]["expires_at"] is None
    assert cached["current"]["ttl_seconds"] is None


def test_initialization_reuses_valid_cached_token(mocker, tmp_path):
    """A valid slot is reused without making token API calls."""
    first_api = Mock()
    first_api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    first_api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    first = _manager(mocker, tmp_path, first_api)

    second_api = Mock()
    mocker.patch.object(token_manager, "ApiTokensApi", return_value=second_api)
    configuration = Configuration(host="https://example.com/device-api")
    configuration.api_key["ApiToken"] = CONFIGURED_TOKEN
    second = TokenManager(CONFIGURED_TOKEN, configuration, request_timeout=1, token_dir=tmp_path)

    second_api.get_api_token_by_snippet.assert_not_called()
    second_api.create_api_token.assert_not_called()
    assert second._configuration.api_key["ApiToken"] == first._configuration.api_key["ApiToken"]


def test_initialization_uses_configured_token_when_token_api_is_unavailable(mocker, tmp_path):
    """A server without token management remains usable with the configured token."""
    api = Mock()
    api.get_api_token_by_snippet.side_effect = NotFoundException()

    manager = _manager(mocker, tmp_path, api)
    manager.start()

    assert manager._configuration.api_key["ApiToken"] == CONFIGURED_TOKEN
    assert manager._thread is None
    assert manager._available is False
    api.create_api_token.assert_not_called()


def test_name_lookup_uses_snippet_endpoint_and_enforces_length(mocker, tmp_path):
    """Token naming uses the by-snippet endpoint and stays within 64 characters."""
    api = Mock()
    long_name = "x" * 64
    api.get_api_token_by_snippet.return_value = _expiring_metadata(long_name, CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token(f"{'x' * 57} abc123", "api_working_token_one", NOW)
    mocker.patch.object(token_manager.secrets, "token_hex", return_value="abc123")

    _manager(mocker, tmp_path, api)

    api.get_api_token_by_snippet.assert_called_once_with(CONFIGURED_TOKEN[:20], _request_timeout=1)
    request = api.create_api_token.call_args.args[0]
    assert request.name == f"{'x' * 57} abc123"
    assert len(request.name) == TOKEN_NAME_MAX_LENGTH


def test_refresh_rotates_and_cleans_up_previous_token(mocker, tmp_path):
    """When refresh is due, revoke previous, demote current, and mint a replacement."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)
    api.reset_mock()
    old_slot = json.loads(manager._slot_path.read_text())
    old_slot["previous"] = {
        "name": "older token",
        "minted_at": NOW.isoformat(),
    }
    manager._slot_path.write_text(json.dumps(old_slot))
    later = NOW + REFRESH_INTERVAL + timedelta(seconds=1)
    mocker.patch.object(token_manager, "_utc_now", return_value=later)
    api.create_api_token.return_value = _created_token("Device token def456", "api_working_token_two", later)

    manager.refresh()

    api.get_api_token_by_snippet.assert_not_called()
    api.delete_api_token.assert_called_once_with("older token", _request_timeout=1)
    cached = json.loads(manager._slot_path.read_text())
    assert cached["base_name"] == "Device token"
    assert cached["current"]["raw_key"] == "api_working_token_two"
    assert cached["previous"]["name"] == "Device token abc123"


def test_refresh_interval_is_observed_ttl_over_thirty(mocker, tmp_path):
    """Refresh becomes due after one-thirtieth of the working token's server lifetime."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)
    api.reset_mock()

    before_due = NOW + REFRESH_INTERVAL - timedelta(seconds=1)
    mocker.patch.object(token_manager, "_utc_now", return_value=before_due)
    assert manager.refresh() is True
    api.create_api_token.assert_not_called()

    after_due = NOW + REFRESH_INTERVAL + timedelta(seconds=1)
    mocker.patch.object(token_manager, "_utc_now", return_value=after_due)
    api.create_api_token.return_value = _created_token("Device token def456", "api_working_token_two", after_due)
    assert manager.refresh() is True
    api.create_api_token.assert_called_once()


def test_refresh_continues_rotation_when_previous_delete_fails(mocker, tmp_path):
    """A failed previous revoke does not block minting the next working token."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)
    slot = json.loads(manager._slot_path.read_text())
    slot["previous"] = {
        "name": "older token",
        "minted_at": NOW.isoformat(),
    }
    manager._slot_path.write_text(json.dumps(slot))
    later = NOW + REFRESH_INTERVAL + timedelta(seconds=1)
    mocker.patch.object(token_manager, "_utc_now", return_value=later)
    api.reset_mock()
    api.delete_api_token.side_effect = ApiException(status=500)
    api.create_api_token.return_value = _created_token("Device token def456", "api_working_token_two", later)

    refresh_succeeded = manager.refresh()

    assert refresh_succeeded
    api.delete_api_token.assert_called_once_with("older token", _request_timeout=1)
    api.create_api_token.assert_called_once()
    cached = json.loads(manager._slot_path.read_text())
    assert cached["current"]["raw_key"] == "api_working_token_two"
    assert cached["previous"]["name"] == "Device token abc123"


def test_refresh_thread_backs_off_after_failed_cycle(mocker, tmp_path):
    """A failed refresh waits a short backoff instead of immediately retrying."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)
    mocker.patch.object(token_manager, "_utc_now", return_value=NOW + REFRESH_INTERVAL + timedelta(seconds=1))
    mocker.patch.object(manager, "refresh", return_value=False)
    stop_event = Mock()
    stop_event.is_set.return_value = False
    stop_event.wait.side_effect = [False, True]
    manager._stop_event = stop_event

    manager._run()

    assert stop_event.wait.call_args_list == [call(0.0), call(REFRESH_RETRY_BACKOFF_SECONDS)]


def test_close_waits_for_refresh_thread_before_closing_client(mocker, tmp_path):
    """Closing waits for in-flight refresh work before closing its HTTP client."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)
    thread = Mock()
    manager._thread = thread
    rotation_client_close = mocker.patch.object(manager._rotation_client, "close")

    manager.close()

    thread.join.assert_called_once_with()
    rotation_client_close.assert_called_once_with()


def test_unauthorized_recovery_uses_newer_token_from_disk(mocker, tmp_path):
    """A 401 reloads a token another process already wrote instead of minting again."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)
    api.reset_mock()

    slot = json.loads(manager._slot_path.read_text())
    slot["current"]["raw_key"] = "api_newer_process_token"
    slot["current"]["snippet"] = "api_newer_process_to"
    manager._slot_path.write_text(json.dumps(slot))

    manager.recover_from_unauthorized()

    assert manager._configuration.api_key["ApiToken"] == "api_newer_process_token"
    api.create_api_token.assert_not_called()


def test_initialization_surfaces_unauthorized_detail(mocker, tmp_path):
    """A 401 during configured-token lookup raises with the server's response body."""
    api = Mock()
    api.get_api_token_by_snippet.side_effect = UnauthorizedException(
        http_resp=SimpleNamespace(
            status=401,
            reason="Unauthorized",
            data="The API token has expired",
            getheaders=lambda: {},
        )
    )

    with pytest.raises(TokenManagerError, match="The API token has expired"):
        _manager(mocker, tmp_path, api)


def test_unauthorized_recovery_raises_when_no_fresher_token_available(mocker, tmp_path):
    """A rejected cached token raises loudly when no fresher token is on disk."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)

    with pytest.raises(TokenManagerError, match="API identity has been revoked"):
        manager.recover_from_unauthorized("API identity has been revoked")

    api.create_api_token.assert_called_once()  # only during init, not during recovery


def test_new_token_name_appends_suffix_and_truncates(mocker):
    """Token names append a unique hex suffix and never exceed the column limit."""
    mocker.patch.object(token_manager.secrets, "token_hex", return_value="def456")

    assert TokenManager._new_token_name("Device token") == "Device token def456"
    assert TokenManager._new_token_name("x" * 64) == f"{'x' * 57} def456"
    assert len(TokenManager._new_token_name("x" * 100)) == TOKEN_NAME_MAX_LENGTH


def test_resolve_base_name_strips_existing_suffix(mocker, tmp_path):
    """The base_name established from an existing token has any prior hex suffix stripped."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token abc123", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token("Device token def456", "api_working_token_one", NOW)

    _manager(mocker, tmp_path, api)

    cached = json.loads((tmp_path / f"{CONFIGURED_TOKEN[:20]}.json").read_text())
    assert cached["base_name"] == "Device token"


def test_existing_token_dir_permissions_are_tightened(mocker, tmp_path):
    """An over-permissive existing token directory is tightened to 0700 during initialization."""
    loose_dir = tmp_path / "tokens"
    loose_dir.mkdir()
    loose_dir.chmod(0o777)  # noqa: S103  # intentionally over-permissive to prove it gets tightened
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)

    _manager(mocker, loose_dir, api)

    assert stat.S_IMODE(loose_dir.stat().st_mode) == TOKEN_DIR_MODE


def test_unauthorized_recovery_leaves_active_token_unchanged_when_no_fresher(mocker, tmp_path):
    """A failed 401 recovery raises loudly and leaves the active token unchanged."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)

    with pytest.raises(TokenManagerError, match="API token was rejected"):
        manager.recover_from_unauthorized()

    assert manager._configuration.api_key["ApiToken"] == "api_working_token_one"


def test_invalid_configured_token_cannot_escape_cache_directory(tmp_path):
    """Invalid token snippets are rejected before cache paths are created."""
    configuration = Configuration(host="https://example.com/device-api")

    with pytest.raises(TokenManagerError, match="configured API token has an invalid format"):
        TokenManager("../../outside-token", configuration, request_timeout=1, token_dir=tmp_path)


def test_refresh_interval_uses_server_ttl_and_clamps_non_positive(mocker, tmp_path):
    """Refresh cadence uses server created_at/expires_at and avoids a zero/negative spin."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _expiring_metadata("Device token", CONFIGURED_TOKEN)
    api.create_api_token.return_value = _created_token(
        "Device token abc123",
        "api_working_token_one",
        NOW,
        created_at=NOW + timedelta(minutes=10),
        expires_at=NOW + timedelta(minutes=3),
    )
    manager = _manager(mocker, tmp_path, api)

    assert manager._current is not None
    assert manager._refresh_interval(manager._current) == timedelta(seconds=REFRESH_RETRY_BACKOFF_SECONDS)

    stop_event = Mock()
    stop_event.is_set.return_value = False
    stop_event.wait.side_effect = [True]
    manager._stop_event = stop_event
    mocker.patch.object(manager, "refresh")
    manager._run()

    assert stop_event.wait.call_args_list[0] == call(float(REFRESH_RETRY_BACKOFF_SECONDS))
    manager.refresh.assert_not_called()
