"""Unit tests for the SDK token auto-refresh logic (groundlight.token_refresh).

These tests exercise the refresher against a fake token API and a temp cache dir, so
they never touch the network or the real ~/.groundlight directory.
"""

# pylint: disable=protected-access,too-few-public-methods,unused-argument

import json
import stat
from datetime import timedelta

import pytest
from groundlight.token_refresh import (
    CLEANUP_GRACE_FACTOR,
    RANDOM_SUFFIX_LENGTH,
    REFRESH_INTERVAL_DAYS,
    TOKEN_NAME_MAX_LENGTH,
    TokenRefresher,
    TokenRefreshError,
    _to_iso,
    _utcnow,
    resolve_token_dir,
)
from groundlight_openapi_client.exceptions import NotFoundException, UnauthorizedException

BOOTSTRAP_TOKEN = "api_bootstrapXXXXXXXXXXXXtail"
OWNER_ONLY_MODE = 0o600


class FakeResponse:
    """Mimics a generated openapi model with a to_dict() method."""

    def __init__(self, data: dict):
        self._data = data

    def to_dict(self) -> dict:
        return self._data


class FakeConfiguration:
    def __init__(self, token: str):
        self.api_key = {"ApiToken": token}


class FakeTokensApi:
    """Minimal stand-in for the generated ApiTokensApi."""

    def __init__(self, list_pages=None):
        self.created = []
        self.deleted = []
        self._mint_counter = 0
        # list_pages: list of (results, next) tuples returned by successive list calls
        self._list_pages = list_pages or [([], None)]
        self.unauthorized_until_bootstrap = False
        self.last_auth_token = None

    def create_api_token(self, api_token_request, **kwargs):
        if self.unauthorized_until_bootstrap and self.last_auth_token != BOOTSTRAP_TOKEN:
            raise UnauthorizedException(status=401)
        self._mint_counter += 1
        raw_key = f"api_minted{self._mint_counter:04d}abcdefghij"
        record = {
            "raw_key": raw_key,
            "raw_key_snippet": raw_key[:20],
            "name": api_token_request.name,
            "expires_at": _to_iso(_utcnow() + timedelta(days=30)),
        }
        self.created.append(record)
        return FakeResponse(record)

    def delete_api_token(self, name, **kwargs):
        self.deleted.append(name)

    def list_api_tokens(self, page=1, **kwargs):
        results, next_url = self._list_pages[min(page - 1, len(self._list_pages) - 1)]
        return FakeResponse({"count": len(results), "next": next_url, "results": results})

    def get_api_token_by_snippet(self, snippet, **kwargs):
        raise NotFoundException(status=404)


def _make_refresher(tmp_path, tokens_api=None, config=None) -> TokenRefresher:
    tokens_api = tokens_api or FakeTokensApi()
    config = config or FakeConfiguration(BOOTSTRAP_TOKEN)
    return TokenRefresher(tokens_api, config, BOOTSTRAP_TOKEN, token_dir=tmp_path)


def test_resolve_token_dir_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("GROUNDLIGHT_TOKEN_DIR", str(tmp_path / "custom"))
    assert resolve_token_dir() == tmp_path / "custom"


def test_generate_token_name_appends_suffix(tmp_path):
    refresher = _make_refresher(tmp_path)
    name = refresher._generate_token_name("My Token")
    assert name.startswith("My Token ")
    base, suffix = name.rsplit(" ", 1)
    assert base == "My Token"
    assert len(suffix) == RANDOM_SUFFIX_LENGTH
    assert all(c in "0123456789abcdef" for c in suffix)


def test_generate_token_name_truncates_long_base(tmp_path):
    refresher = _make_refresher(tmp_path)
    name = refresher._generate_token_name("z" * 200)
    assert len(name) <= TOKEN_NAME_MAX_LENGTH


def test_bootstrap_mints_and_persists_when_no_cache(tmp_path):
    tokens_api = FakeTokensApi()
    config = FakeConfiguration(BOOTSTRAP_TOKEN)
    refresher = _make_refresher(tmp_path, tokens_api, config)

    refresher.bootstrap()

    assert len(tokens_api.created) == 1
    minted = tokens_api.created[0]
    # The client's active token is now the minted working token, not the bootstrap token.
    assert config.api_key["ApiToken"] == minted["raw_key"]

    slot = json.loads((tmp_path / f"{BOOTSTRAP_TOKEN[:20]}.json").read_text())
    assert slot["current"]["raw_key"] == minted["raw_key"]
    assert slot["previous"] is None


def test_bootstrap_uses_valid_cache_without_minting(tmp_path):
    tokens_api = FakeTokensApi()
    config = FakeConfiguration(BOOTSTRAP_TOKEN)
    refresher = _make_refresher(tmp_path, tokens_api, config)
    refresher._ensure_token_dir()
    refresher._write_slot(
        current={
            "raw_key": "api_cachedtokenvalue0000",
            "snippet": "api_cachedtokenvalue",
            "name": "cached",
            "expires_at": _to_iso(_utcnow() + timedelta(days=10)),
            "minted_at": _to_iso(_utcnow()),
        },
        previous=None,
    )

    refresher.bootstrap()

    assert not tokens_api.created
    assert config.api_key["ApiToken"] == "api_cachedtokenvalue0000"


def test_bootstrap_remints_when_cache_expired(tmp_path):
    tokens_api = FakeTokensApi()
    config = FakeConfiguration(BOOTSTRAP_TOKEN)
    refresher = _make_refresher(tmp_path, tokens_api, config)
    refresher._ensure_token_dir()
    refresher._write_slot(
        current={
            "raw_key": "api_expiredtoken00000000",
            "snippet": "api_expiredtoken0000",
            "name": "expired",
            "expires_at": _to_iso(_utcnow() - timedelta(days=1)),
            "minted_at": _to_iso(_utcnow() - timedelta(days=31)),
        },
        previous=None,
    )

    refresher.bootstrap()

    assert len(tokens_api.created) == 1
    assert config.api_key["ApiToken"] == tokens_api.created[0]["raw_key"]


def test_bootstrap_degrades_when_endpoint_missing(tmp_path):
    class MissingEndpointApi(FakeTokensApi):
        def list_api_tokens(self, page=1, **kwargs):
            raise NotFoundException(status=404)

        def create_api_token(self, api_token_request, **kwargs):
            raise NotFoundException(status=404)

    config = FakeConfiguration(BOOTSTRAP_TOKEN)
    refresher = _make_refresher(tmp_path, MissingEndpointApi(), config)

    refresher.bootstrap()

    # Falls back to the bootstrap token and disables rotation; no thread is started.
    assert config.api_key["ApiToken"] == BOOTSTRAP_TOKEN
    assert refresher._enabled is False
    refresher.start()
    assert refresher._thread is None


def test_bootstrap_raises_on_unauthorized(tmp_path):
    class UnauthorizedApi(FakeTokensApi):
        def list_api_tokens(self, page=1, **kwargs):
            raise UnauthorizedException(status=401)

        def create_api_token(self, api_token_request, **kwargs):
            raise UnauthorizedException(status=401)

    refresher = _make_refresher(tmp_path, UnauthorizedApi())
    with pytest.raises(TokenRefreshError):
        refresher.bootstrap()


def test_bootstrap_raises_on_mint_failure(tmp_path):
    class BrokenTokensApi(FakeTokensApi):
        def create_api_token(self, api_token_request, **kwargs):
            raise RuntimeError("network down")

    refresher = _make_refresher(tmp_path, BrokenTokensApi())
    with pytest.raises(TokenRefreshError):
        refresher.bootstrap()


def test_lookup_current_name_matches_snippet_across_pages(tmp_path):
    active = "api_minted0001abcdefghij"
    pages = [
        ([{"raw_key_snippet": "api_someoneelse00000", "name": "other"}], "http://next"),
        ([{"raw_key_snippet": active[:20], "name": "mine"}], None),
    ]
    tokens_api = FakeTokensApi(list_pages=pages)
    config = FakeConfiguration(active)
    refresher = _make_refresher(tmp_path, tokens_api, config)

    assert refresher._lookup_current_name() == "mine"


def test_lookup_current_name_returns_none_when_absent(tmp_path):
    pages = [([{"raw_key_snippet": "api_nomatchhere00000", "name": "other"}], None)]
    tokens_api = FakeTokensApi(list_pages=pages)
    config = FakeConfiguration("api_minted0001abcdefghij")
    refresher = _make_refresher(tmp_path, tokens_api, config)

    assert refresher._lookup_current_name() is None


def test_refresh_demotes_current_to_previous(tmp_path):
    active = "api_minted0001abcdefghij"
    pages = [([{"raw_key_snippet": active[:20], "name": "My Token"}], None)]
    tokens_api = FakeTokensApi(list_pages=pages)
    config = FakeConfiguration(active)
    refresher = _make_refresher(tmp_path, tokens_api, config)
    refresher._ensure_token_dir()

    old_current = {
        "raw_key": active,
        "snippet": active[:20],
        "name": "My Token",
        "expires_at": _to_iso(_utcnow() + timedelta(days=29)),
        "minted_at": _to_iso(_utcnow()),
    }
    refresher._refresh(previous_current=old_current)

    slot = json.loads((tmp_path / f"{BOOTSTRAP_TOKEN[:20]}.json").read_text())
    assert slot["current"]["name"].startswith("My Token ")
    assert slot["previous"]["name"] == "My Token"
    assert config.api_key["ApiToken"] == slot["current"]["raw_key"]


def test_cleanup_previous_deletes_after_grace(tmp_path):
    refresher = _make_refresher(tmp_path)
    refresher._ensure_token_dir()
    stale_minted = _utcnow() - timedelta(days=CLEANUP_GRACE_FACTOR * REFRESH_INTERVAL_DAYS + 1)
    refresher._write_slot(
        current={
            "raw_key": "cur",
            "snippet": "cur",
            "name": "cur",
            "expires_at": _to_iso(_utcnow()),
            "minted_at": _to_iso(_utcnow()),
        },
        previous={"name": "old-token", "minted_at": _to_iso(stale_minted)},
    )

    refresher._cleanup_previous()

    assert refresher._tokens_api.deleted == ["old-token"]
    slot = json.loads((tmp_path / f"{BOOTSTRAP_TOKEN[:20]}.json").read_text())
    assert slot["previous"] is None


def test_cleanup_previous_skips_within_grace(tmp_path):
    refresher = _make_refresher(tmp_path)
    refresher._ensure_token_dir()
    refresher._write_slot(
        current={
            "raw_key": "cur",
            "snippet": "cur",
            "name": "cur",
            "expires_at": _to_iso(_utcnow()),
            "minted_at": _to_iso(_utcnow()),
        },
        previous={"name": "recent-token", "minted_at": _to_iso(_utcnow())},
    )

    refresher._cleanup_previous()

    assert not refresher._tokens_api.deleted


def test_cleanup_previous_treats_missing_as_gone(tmp_path):
    class DeleteNotFoundApi(FakeTokensApi):
        def delete_api_token(self, name, **kwargs):
            raise NotFoundException(status=404)

    refresher = _make_refresher(tmp_path, DeleteNotFoundApi())
    refresher._ensure_token_dir()
    stale_minted = _utcnow() - timedelta(days=CLEANUP_GRACE_FACTOR * REFRESH_INTERVAL_DAYS + 1)
    refresher._write_slot(
        current={
            "raw_key": "cur",
            "snippet": "cur",
            "name": "cur",
            "expires_at": _to_iso(_utcnow()),
            "minted_at": _to_iso(_utcnow()),
        },
        previous={"name": "gone", "minted_at": _to_iso(stale_minted)},
    )

    refresher._cleanup_previous()  # should not raise

    slot = json.loads((tmp_path / f"{BOOTSTRAP_TOKEN[:20]}.json").read_text())
    assert slot["previous"] is None


def test_mint_falls_back_to_bootstrap_on_unauthorized(tmp_path):
    tokens_api = FakeTokensApi()
    tokens_api.unauthorized_until_bootstrap = True
    config = FakeConfiguration("api_staletoken0000000000")

    def track_token(raw_key):
        config.api_key["ApiToken"] = raw_key
        tokens_api.last_auth_token = raw_key

    refresher = _make_refresher(tmp_path, tokens_api, config)
    refresher._set_active_token = track_token  # capture which token authenticates the mint
    tokens_api.last_auth_token = config.api_key["ApiToken"]

    result = refresher._mint("some-name")

    assert result["raw_key"] == tokens_api.created[0]["raw_key"]


def test_slot_file_written_with_owner_only_permissions(tmp_path):
    refresher = _make_refresher(tmp_path)
    refresher._ensure_token_dir()
    refresher._write_slot(current={"raw_key": "x"}, previous=None)

    mode = stat.S_IMODE((tmp_path / f"{BOOTSTRAP_TOKEN[:20]}.json").stat().st_mode)
    assert mode == OWNER_ONLY_MODE
