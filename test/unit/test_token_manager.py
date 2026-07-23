# pylint: disable=protected-access
import json
import stat
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest
from groundlight import token_manager
from groundlight.token_manager import (
    REFRESH_INTERVAL_DAYS,
    REFRESH_RETRY_BACKOFF_SECONDS,
    TOKEN_NAME_MAX_LENGTH,
    TOKEN_TTL_DAYS,
    TokenManager,
    TokenManagerError,
)
from groundlight_openapi_client import Configuration
from groundlight_openapi_client.exceptions import ApiException, NotFoundException, UnauthorizedException

BOOTSTRAP_TOKEN = "api_bootstrap_token_value_long_enough"
NOW = datetime(2026, 7, 9, 12, 0, tzinfo=timezone.utc)
TOKEN_CACHE_MODE = 0o600
TOKEN_DIR_MODE = 0o700


def _metadata(name: str, raw_key: str) -> SimpleNamespace:
    """Build the token metadata returned by snippet or list operations."""
    return SimpleNamespace(name=name, raw_key_snippet=raw_key[:20])


def _created_token(name: str, raw_key: str, now: datetime) -> SimpleNamespace:
    """Build a token creation response."""
    return SimpleNamespace(
        name=name,
        raw_key=raw_key,
        raw_key_snippet=raw_key[:20],
        expires_at=now + timedelta(days=TOKEN_TTL_DAYS),
    )


def _manager(mocker, tmp_path, api, now=NOW) -> TokenManager:
    """Create a token manager with deterministic API and time dependencies."""
    mocker.patch.object(token_manager, "ApiTokensApi", return_value=api)
    mocker.patch.object(token_manager, "_utc_now", return_value=now)
    configuration = Configuration(host="https://example.com/device-api")
    configuration.api_key["ApiToken"] = BOOTSTRAP_TOKEN
    return TokenManager(
        bootstrap_token=BOOTSTRAP_TOKEN,
        configuration=configuration,
        request_timeout=1,
        token_dir=tmp_path,
    )


def test_initialization_mints_and_privately_caches_token(mocker, tmp_path):
    """A missing slot is minted from the bootstrap token and stored with mode 0600."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _metadata("Device token", BOOTSTRAP_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)

    manager = _manager(mocker, tmp_path, api)

    request = api.create_api_token.call_args.args[0]
    assert request.name.startswith("Device token ")
    assert request.expires_at == NOW + timedelta(days=TOKEN_TTL_DAYS)
    assert manager._configuration.api_key["ApiToken"] == "api_working_token_one"
    assert stat.S_IMODE(manager._slot_path.stat().st_mode) == TOKEN_CACHE_MODE
    cached = json.loads(manager._slot_path.read_text())
    assert cached["base_name"] == "Device token"
    assert cached["current"]["raw_key"] == "api_working_token_one"
    assert cached["previous"]["name"] == "Device token"
    api.delete_api_token.assert_not_called()


def test_initialization_parks_bootstrap_token_as_previous(mocker, tmp_path):
    """After minting the first working token, the bootstrap token is parked as previous (not revoked)."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _metadata("Device token", BOOTSTRAP_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)

    manager = _manager(mocker, tmp_path, api)

    api.delete_api_token.assert_not_called()
    cached = json.loads(manager._slot_path.read_text())
    assert cached["previous"]["name"] == "Device token"
    assert cached["previous"]["minted_at"] == NOW.isoformat().replace("+00:00", "Z")


def test_initialization_reuses_valid_cached_token(mocker, tmp_path):
    """A valid slot is reused without making token API calls."""
    first_api = Mock()
    first_api.get_api_token_by_snippet.return_value = _metadata("Device token", BOOTSTRAP_TOKEN)
    first_api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    first = _manager(mocker, tmp_path, first_api)

    second_api = Mock()
    mocker.patch.object(token_manager, "ApiTokensApi", return_value=second_api)
    configuration = Configuration(host="https://example.com/device-api")
    configuration.api_key["ApiToken"] = BOOTSTRAP_TOKEN
    second = TokenManager(BOOTSTRAP_TOKEN, configuration, request_timeout=1, token_dir=tmp_path)

    second_api.get_api_token_by_snippet.assert_not_called()
    second_api.create_api_token.assert_not_called()
    assert second._configuration.api_key["ApiToken"] == first._configuration.api_key["ApiToken"]


def test_initialization_uses_bootstrap_when_token_api_is_unavailable(mocker, tmp_path):
    """A server without token management remains usable with the bootstrap token."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _metadata("Device token", BOOTSTRAP_TOKEN)
    api.create_api_token.side_effect = NotFoundException()

    manager = _manager(mocker, tmp_path, api)
    manager.start()

    assert manager._configuration.api_key["ApiToken"] == BOOTSTRAP_TOKEN
    assert manager._thread is None
    api.create_api_token.assert_called_once()


def test_name_lookup_uses_snippet_endpoint_and_enforces_length(mocker, tmp_path):
    """Token naming uses the by-snippet endpoint (no pagination) and stays within 64 characters."""
    api = Mock()
    long_name = "x" * 64
    api.get_api_token_by_snippet.return_value = _metadata(long_name, BOOTSTRAP_TOKEN)
    api.create_api_token.return_value = _created_token(f"{'x' * 57} abc123", "api_working_token_one", NOW)
    mocker.patch.object(token_manager.secrets, "token_hex", return_value="abc123")

    _manager(mocker, tmp_path, api)

    api.get_api_token_by_snippet.assert_called_once_with(BOOTSTRAP_TOKEN[:20], _request_timeout=1)
    request = api.create_api_token.call_args.args[0]
    assert request.name == f"{'x' * 57} abc123"
    assert len(request.name) == TOKEN_NAME_MAX_LENGTH


def test_refresh_rotates_and_cleans_up_previous_token(mocker, tmp_path):
    """When refresh is due, revoke previous, demote current, and mint a replacement."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _metadata("Device token", BOOTSTRAP_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)
    api.reset_mock()  # clear calls from init (bootstrap lookup + mint)
    old_slot = json.loads(manager._slot_path.read_text())
    old_slot["previous"] = {
        "name": "older token",
        "minted_at": NOW.isoformat(),
    }
    manager._slot_path.write_text(json.dumps(old_slot))
    later = NOW + timedelta(days=REFRESH_INTERVAL_DAYS, seconds=1)
    mocker.patch.object(token_manager, "_utc_now", return_value=later)
    api.create_api_token.return_value = _created_token("Device token def456", "api_working_token_two", later)

    manager.refresh()

    # Rotation reads base_name from the slot; no snippet endpoint call is made.
    api.get_api_token_by_snippet.assert_not_called()
    api.delete_api_token.assert_called_once_with("older token", _request_timeout=1)
    cached = json.loads(manager._slot_path.read_text())
    assert cached["base_name"] == "Device token"
    assert cached["current"]["raw_key"] == "api_working_token_two"
    assert cached["previous"]["name"] == "Device token abc123"


def test_refresh_continues_rotation_when_previous_delete_fails(mocker, tmp_path):
    """A failed previous revoke does not block minting the next working token."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _metadata("Device token", BOOTSTRAP_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)
    slot = json.loads(manager._slot_path.read_text())
    slot["previous"] = {
        "name": "older token",
        "minted_at": NOW.isoformat(),
    }
    manager._slot_path.write_text(json.dumps(slot))
    later = NOW + timedelta(days=REFRESH_INTERVAL_DAYS, seconds=1)
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
    """A failed refresh waits a short backoff instead of immediately retrying or waiting a full day."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _metadata("Device token", BOOTSTRAP_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)
    mocker.patch.object(token_manager, "_utc_now", return_value=NOW + timedelta(days=REFRESH_INTERVAL_DAYS, seconds=1))
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
    api.get_api_token_by_snippet.return_value = _metadata("Device token", BOOTSTRAP_TOKEN)
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
    api.get_api_token_by_snippet.return_value = _metadata("Device token", BOOTSTRAP_TOKEN)
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
    """A 401 during bootstrap lookup raises with the server's response body."""
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
    api.get_api_token_by_snippet.return_value = _metadata("Device token", BOOTSTRAP_TOKEN)
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
    # Bootstrap token already has a suffix from a previous rotation cycle.
    api.get_api_token_by_snippet.return_value = _metadata("Device token abc123", BOOTSTRAP_TOKEN)
    api.create_api_token.return_value = _created_token("Device token def456", "api_working_token_one", NOW)

    _manager(mocker, tmp_path, api)

    cached = json.loads((tmp_path / f"{BOOTSTRAP_TOKEN[:20]}.json").read_text())
    assert cached["base_name"] == "Device token"


def test_existing_token_dir_permissions_are_tightened(mocker, tmp_path):
    """An over-permissive existing token directory is tightened to 0700 during initialization."""
    loose_dir = tmp_path / "tokens"
    loose_dir.mkdir()
    loose_dir.chmod(0o777)  # noqa: S103  # intentionally over-permissive to prove it gets tightened
    api = Mock()
    api.get_api_token_by_snippet.return_value = _metadata("Device token", BOOTSTRAP_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)

    _manager(mocker, loose_dir, api)

    assert stat.S_IMODE(loose_dir.stat().st_mode) == TOKEN_DIR_MODE


def test_unauthorized_recovery_restores_previous_token_when_remint_fails(mocker, tmp_path):
    """A failed 401 recovery raises loudly and leaves the active token unchanged."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _metadata("Device token", BOOTSTRAP_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)

    with pytest.raises(TokenManagerError, match="API token was rejected"):
        manager.recover_from_unauthorized()

    assert manager._configuration.api_key["ApiToken"] == "api_working_token_one"


def test_invalid_bootstrap_token_cannot_escape_cache_directory(tmp_path):
    """Invalid token snippets are rejected before cache paths are created."""
    configuration = Configuration(host="https://example.com/device-api")

    with pytest.raises(TokenManagerError, match="configured API token has an invalid format"):
        TokenManager("../../outside-token", configuration, request_timeout=1, token_dir=tmp_path)


def test_refresh_falls_back_to_snippet_endpoint_for_old_format_slot(mocker, tmp_path):
    """A slot written before the base_name field existed triggers a snippet lookup on the next refresh."""
    api = Mock()
    api.get_api_token_by_snippet.return_value = _metadata("Device token", BOOTSTRAP_TOKEN)
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)
    api.reset_mock()

    # Simulate a slot written by an older SDK version (no base_name field).
    slot_data = json.loads(manager._slot_path.read_text())
    del slot_data["base_name"]
    manager._slot_path.write_text(json.dumps(slot_data))

    later = NOW + timedelta(days=REFRESH_INTERVAL_DAYS, seconds=1)
    mocker.patch.object(token_manager, "_utc_now", return_value=later)
    api.get_api_token_by_snippet.return_value = _metadata("Device token abc123", "api_working_token_one")
    api.create_api_token.return_value = _created_token("Device token def456", "api_working_token_two", later)

    manager.refresh()

    # Fallback lookup was needed because base_name was absent.
    api.get_api_token_by_snippet.assert_called_once()
    cached = json.loads(manager._slot_path.read_text())
    # After the refresh the slot has base_name for future rotations.
    assert cached["base_name"] == "Device token"
    assert cached["current"]["raw_key"] == "api_working_token_two"
