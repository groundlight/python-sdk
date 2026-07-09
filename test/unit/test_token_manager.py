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
    REFRESH_INTERVAL_SECONDS,
    TOKEN_NAME_MAX_LENGTH,
    TOKEN_TTL_DAYS,
    TokenManager,
    TokenManagerError,
)
from groundlight_openapi_client import Configuration
from groundlight_openapi_client.exceptions import ApiException

BOOTSTRAP_TOKEN = "api_bootstrap_token_value_long_enough"
NOW = datetime(2026, 7, 9, 12, 0, tzinfo=timezone.utc)
TOKEN_CACHE_MODE = 0o600
EXPECTED_PAGE_COUNT = 2


def _metadata(name: str, raw_key: str) -> SimpleNamespace:
    """Build the token metadata returned by list operations."""
    return SimpleNamespace(name=name, raw_key_snippet=raw_key[:20])


def _created_token(name: str, raw_key: str, now: datetime) -> SimpleNamespace:
    """Build a token creation response."""
    return SimpleNamespace(
        name=name,
        raw_key=raw_key,
        raw_key_snippet=raw_key[:20],
        expires_at=now + timedelta(days=TOKEN_TTL_DAYS),
    )


def _page(results, next_url=None) -> SimpleNamespace:
    """Build one page of token metadata."""
    return SimpleNamespace(results=results, next=next_url)


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
    api.list_api_tokens.return_value = _page([_metadata("Device token", BOOTSTRAP_TOKEN)])
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)

    manager = _manager(mocker, tmp_path, api)

    request = api.create_api_token.call_args.args[0]
    assert request.name.startswith("Device token ")
    assert request.expires_at == NOW + timedelta(days=TOKEN_TTL_DAYS)
    assert manager._configuration.api_key["ApiToken"] == "api_working_token_one"
    assert stat.S_IMODE(manager._slot_path.stat().st_mode) == TOKEN_CACHE_MODE
    cached = json.loads(manager._slot_path.read_text())
    assert cached["current"]["raw_key"] == "api_working_token_one"
    assert cached["previous"] is None


def test_initialization_reuses_valid_cached_token(mocker, tmp_path):
    """A valid slot is reused without making token API calls."""
    first_api = Mock()
    first_api.list_api_tokens.return_value = _page([_metadata("Device token", BOOTSTRAP_TOKEN)])
    first_api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    first = _manager(mocker, tmp_path, first_api)

    second_api = Mock()
    mocker.patch.object(token_manager, "ApiTokensApi", return_value=second_api)
    configuration = Configuration(host="https://example.com/device-api")
    configuration.api_key["ApiToken"] = BOOTSTRAP_TOKEN
    second = TokenManager(BOOTSTRAP_TOKEN, configuration, request_timeout=1, token_dir=tmp_path)

    second_api.list_api_tokens.assert_not_called()
    second_api.create_api_token.assert_not_called()
    assert second._configuration.api_key["ApiToken"] == first._configuration.api_key["ApiToken"]


def test_name_lookup_follows_pagination_and_enforces_length(mocker, tmp_path):
    """Token naming finds the matching snippet on later pages and stays within 64 characters."""
    api = Mock()
    long_name = "x" * 64
    api.list_api_tokens.side_effect = [
        _page([_metadata("Other token", "api_other_token_value")], "https://example.com/page=2"),
        _page([_metadata(long_name, BOOTSTRAP_TOKEN)]),
    ]
    api.create_api_token.return_value = _created_token(f"{'x' * 57} abc123", "api_working_token_one", NOW)
    mocker.patch.object(token_manager.secrets, "token_hex", return_value="abc123")

    _manager(mocker, tmp_path, api)

    assert api.list_api_tokens.call_count == EXPECTED_PAGE_COUNT
    request = api.create_api_token.call_args.args[0]
    assert request.name == f"{'x' * 57} abc123"
    assert len(request.name) == TOKEN_NAME_MAX_LENGTH


def test_refresh_rotates_and_cleans_up_previous_token(mocker, tmp_path):
    """Scheduled refresh revokes an old previous token and records the replaced current token."""
    api = Mock()
    api.list_api_tokens.return_value = _page([_metadata("Device token", BOOTSTRAP_TOKEN)])
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)

    old_slot = json.loads(manager._slot_path.read_text())
    old_slot["previous"] = {
        "name": "older token",
        "minted_at": (NOW - timedelta(days=2)).isoformat(),
    }
    manager._slot_path.write_text(json.dumps(old_slot))
    later = NOW + timedelta(days=REFRESH_INTERVAL_DAYS, seconds=1)
    mocker.patch.object(token_manager, "_utc_now", return_value=later)
    api.list_api_tokens.return_value = _page([_metadata("Device token abc123", "api_working_token_one")])
    api.create_api_token.return_value = _created_token("Device token def456", "api_working_token_two", later)

    manager.refresh()

    api.delete_api_token.assert_called_once_with("older token", _request_timeout=1)
    cached = json.loads(manager._slot_path.read_text())
    assert cached["current"]["raw_key"] == "api_working_token_two"
    assert cached["previous"]["name"] == "Device token abc123"


def test_refresh_preserves_cleanup_metadata_when_deletion_fails(mocker, tmp_path):
    """A failed cleanup postpones minting so the deletion can be retried later."""
    api = Mock()
    api.list_api_tokens.return_value = _page([_metadata("Device token", BOOTSTRAP_TOKEN)])
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)
    slot = json.loads(manager._slot_path.read_text())
    slot["previous"] = {
        "name": "older token",
        "minted_at": (NOW - timedelta(days=2)).isoformat(),
    }
    manager._slot_path.write_text(json.dumps(slot))
    mocker.patch.object(token_manager, "_utc_now", return_value=NOW + timedelta(days=REFRESH_INTERVAL_DAYS, seconds=1))
    api.reset_mock()
    api.delete_api_token.side_effect = ApiException(status=500)

    refresh_succeeded = manager.refresh()

    assert not refresh_succeeded
    api.create_api_token.assert_not_called()
    cached = json.loads(manager._slot_path.read_text())
    assert cached["previous"]["name"] == "older token"
    assert cached["current"]["raw_key"] == "api_working_token_one"


def test_refresh_thread_backs_off_after_failed_cycle(mocker, tmp_path):
    """A failed refresh waits one interval instead of immediately retrying."""
    api = Mock()
    api.list_api_tokens.return_value = _page([_metadata("Device token", BOOTSTRAP_TOKEN)])
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)
    mocker.patch.object(token_manager, "_utc_now", return_value=NOW + timedelta(days=REFRESH_INTERVAL_DAYS, seconds=1))
    mocker.patch.object(manager, "refresh", return_value=False)
    stop_event = Mock()
    stop_event.is_set.return_value = False
    stop_event.wait.side_effect = [False, True]
    manager._stop_event = stop_event

    manager._run()

    assert stop_event.wait.call_args_list == [call(0.0), call(REFRESH_INTERVAL_SECONDS)]


def test_unauthorized_recovery_uses_newer_token_from_disk(mocker, tmp_path):
    """A 401 reloads a token another process already wrote instead of minting again."""
    api = Mock()
    api.list_api_tokens.return_value = _page([_metadata("Device token", BOOTSTRAP_TOKEN)])
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


def test_unauthorized_recovery_mints_with_bootstrap_token(mocker, tmp_path):
    """A rejected cached token is replaced using the unchanged bootstrap credential."""
    api = Mock()
    api.list_api_tokens.return_value = _page([_metadata("Device token", BOOTSTRAP_TOKEN)])
    api.create_api_token.return_value = _created_token("Device token abc123", "api_working_token_one", NOW)
    manager = _manager(mocker, tmp_path, api)
    api.reset_mock()
    slot = json.loads(manager._slot_path.read_text())
    slot["previous"] = {
        "name": "older token",
        "minted_at": (NOW - timedelta(days=1)).isoformat(),
    }
    manager._slot_path.write_text(json.dumps(slot))
    api.list_api_tokens.return_value = _page([_metadata("Device token abc123", "api_working_token_one")])
    api.create_api_token.return_value = _created_token("Device token def456", "api_working_token_two", NOW)

    manager.recover_from_unauthorized()

    api.create_api_token.assert_called_once()
    assert manager._configuration.api_key["ApiToken"] == "api_working_token_two"
    cached = json.loads(manager._slot_path.read_text())
    assert cached["previous"]["name"] == "older token"


def test_invalid_bootstrap_token_cannot_escape_cache_directory(tmp_path):
    """Invalid token snippets are rejected before cache paths are created."""
    configuration = Configuration(host="https://example.com/device-api")

    with pytest.raises(TokenManagerError, match="invalid format"):
        TokenManager("../../outside-token", configuration, request_timeout=1, token_dir=tmp_path)
