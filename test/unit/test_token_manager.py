"""Unit tests for disk-backed API token refresh."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from unittest.mock import MagicMock

import pytest
from groundlight.token_manager import (
    TOKEN_TTL_DAYS,
    CachedToken,
    PreviousToken,
    TokenManager,
    TokenSlot,
    _next_token_name,
    token_snippet,
)
from groundlight_openapi_client.exceptions import NotFoundException


def _utc(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


class FakeApiTokensApi:
    """In-memory stand-in for ApiTokensApi."""

    def __init__(self) -> None:
        self.tokens: list[dict[str, Any]] = []
        self.deleted: list[str] = []
        self.create_calls = 0
        self.list_calls = 0
        self.by_snippet_calls = 0

    def seed(self, name: str, raw_key: str, expires_at: Optional[datetime] = None) -> None:
        self.tokens.append({
            "name": name,
            "raw_key": raw_key,
            "raw_key_snippet": token_snippet(raw_key),
            "expires_at": expires_at or (_utc(2099, 1, 1)),
        })

    def list_api_tokens(self, page: int = 1, page_size: int = 100, **kwargs):  # pylint: disable=unused-argument
        self.list_calls += 1
        start = (page - 1) * page_size
        end = start + page_size
        page_tokens = self.tokens[start:end]
        response = MagicMock()
        response.results = [MagicMock(**{k: v for k, v in t.items() if k != "raw_key"}) for t in page_tokens]
        for mock_token, raw in zip(response.results, page_tokens):
            mock_token.raw_key_snippet = raw["raw_key_snippet"]
            mock_token.name = raw["name"]
        response.next = "next" if end < len(self.tokens) else None
        return response

    def create_api_token(self, api_token_request, **kwargs):  # pylint: disable=unused-argument
        self.create_calls += 1
        raw_key = f"api_minted_{self.create_calls:04d}_{'x' * 40}"
        token = {
            "name": api_token_request.name,
            "raw_key": raw_key,
            "raw_key_snippet": token_snippet(raw_key),
            "expires_at": api_token_request.expires_at,
        }
        self.tokens.append(token)
        created = MagicMock()
        created.name = token["name"]
        created.raw_key = token["raw_key"]
        created.raw_key_snippet = token["raw_key_snippet"]
        created.expires_at = token["expires_at"]
        return created

    def delete_api_token(self, name: str, **kwargs):  # pylint: disable=unused-argument
        self.deleted.append(name)
        self.tokens = [t for t in self.tokens if t["name"] != name]

    def get_api_token_by_snippet(self, snippet: str, **kwargs):  # pylint: disable=unused-argument
        self.by_snippet_calls += 1
        for token in self.tokens:
            if token["raw_key_snippet"] == snippet:
                found = MagicMock()
                found.name = token["name"]
                found.raw_key_snippet = token["raw_key_snippet"]
                return found
        raise NotFoundException(status=404, reason="Not found")


@pytest.fixture(name="bootstrap")
def fixture_bootstrap() -> str:
    return "api_bootstrap_token_abcdefghijklmnop"


@pytest.fixture(name="api")
def fixture_api(bootstrap: str) -> FakeApiTokensApi:
    api = FakeApiTokensApi()
    api.seed("Bootstrap Token", bootstrap)
    return api


def test_token_snippet_uses_first_20_chars(bootstrap: str):
    assert token_snippet(bootstrap) == bootstrap[:20]
    assert len(token_snippet(bootstrap)) == 20  # noqa: PLR2004


def test_next_token_name_truncates_long_base():
    long_name = "A" * 64
    result = _next_token_name(long_name)
    assert len(result) == 64  # noqa: PLR2004
    assert result.startswith("A" * 57)
    assert result[57] == " "


def test_next_token_name_fallback_when_missing():
    result = _next_token_name(None)
    assert result.startswith("sdk-auto ")
    assert len(result) == len("sdk-auto ") + 6


def test_manager_mints_when_cache_missing(tmp_path, bootstrap: str, api: FakeApiTokensApi):
    installed: list[str] = []
    manager = TokenManager(
        bootstrap_token=bootstrap,
        api_tokens_api=api,  # type: ignore[arg-type]
        set_api_token=installed.append,
        token_dir=tmp_path,
        refresh_interval=timedelta(days=30),
        token_ttl=timedelta(days=TOKEN_TTL_DAYS),
    )
    try:
        assert api.create_calls == 1
        assert api.list_calls >= 1
        assert api.by_snippet_calls == 0
        assert manager.working_token.startswith("api_minted_")
        assert installed[-1] == manager.working_token
        slot_path = tmp_path / f"{token_snippet(bootstrap)}.json"
        assert slot_path.exists()
        data = json.loads(slot_path.read_text(encoding="utf-8"))
        assert data["current"]["raw_key"] == manager.working_token
        assert data["previous"] is None
    finally:
        manager.close()


def test_manager_reuses_valid_cache(tmp_path, bootstrap: str, api: FakeApiTokensApi):
    snippet = token_snippet(bootstrap)
    cached_key = "api_cached_token_1234567890abcdef"
    now = datetime.now(timezone.utc)
    slot = TokenSlot(
        current=CachedToken(
            raw_key=cached_key,
            snippet=token_snippet(cached_key),
            name="Cached Token",
            expires_at=now + timedelta(days=TOKEN_TTL_DAYS),
            minted_at=now,
        )
    )
    (tmp_path / f"{snippet}.json").write_text(json.dumps(slot.to_dict()), encoding="utf-8")

    installed: list[str] = []
    manager = TokenManager(
        bootstrap_token=bootstrap,
        api_tokens_api=api,  # type: ignore[arg-type]
        set_api_token=installed.append,
        token_dir=tmp_path,
        refresh_interval=timedelta(days=30),
    )
    try:
        assert api.create_calls == 0
        assert manager.working_token == cached_key
        assert installed[-1] == cached_key
    finally:
        manager.close()


def test_refresh_mints_and_promotes_previous(tmp_path, bootstrap: str, api: FakeApiTokensApi):
    installed: list[str] = []
    manager = TokenManager(
        bootstrap_token=bootstrap,
        api_tokens_api=api,  # type: ignore[arg-type]
        set_api_token=installed.append,
        token_dir=tmp_path,
        refresh_interval=timedelta(days=1),
    )
    try:
        first = manager.working_token
        slot = manager._slot  # pylint: disable=protected-access
        assert slot is not None
        first_name = slot.current.name
        # Make the current token look overdue for refresh.
        slot.current.minted_at = _utc(2020, 1, 1)
        manager._write_slot(slot)  # pylint: disable=protected-access
        manager._refresh_once()  # pylint: disable=protected-access
        assert manager.working_token != first
        updated = manager._slot  # pylint: disable=protected-access
        assert updated is not None
        assert updated.previous is not None
        assert updated.previous.name == first_name
    finally:
        manager.close()


def test_cleanup_deletes_previous_after_grace(tmp_path, bootstrap: str, api: FakeApiTokensApi):
    installed: list[str] = []
    manager = TokenManager(
        bootstrap_token=bootstrap,
        api_tokens_api=api,  # type: ignore[arg-type]
        set_api_token=installed.append,
        token_dir=tmp_path,
        refresh_interval=timedelta(days=1),
    )
    try:
        old_name = "Old Token"
        api.seed(old_name, "api_old_token_xxxxxxxxxxxxxxxx")
        slot = manager._slot  # pylint: disable=protected-access
        assert slot is not None
        slot.previous = PreviousToken(name=old_name, minted_at=_utc(2020, 1, 1))
        slot.current.minted_at = _utc(2020, 1, 3)
        manager._write_slot(slot)  # pylint: disable=protected-access
        manager._refresh_once()  # pylint: disable=protected-access
        assert old_name in api.deleted
    finally:
        manager.close()


def test_get_token_name_by_snippet_exists_but_unused(tmp_path, bootstrap: str, api: FakeApiTokensApi):
    manager = TokenManager(
        bootstrap_token=bootstrap,
        api_tokens_api=api,  # type: ignore[arg-type]
        set_api_token=lambda _token: None,
        token_dir=tmp_path,
        refresh_interval=timedelta(days=30),
    )
    try:
        assert api.by_snippet_calls == 0
        name = manager._get_token_name_by_snippet(token_snippet(bootstrap))  # pylint: disable=protected-access
        assert name == "Bootstrap Token"
        assert api.by_snippet_calls == 1
    finally:
        manager.close()


def test_falls_back_to_bootstrap_when_api_tokens_missing(tmp_path, bootstrap: str):
    api = FakeApiTokensApi()

    def _missing(*_args, **_kwargs):
        raise NotFoundException(status=404, reason="Not found")

    api.list_api_tokens = _missing  # type: ignore[method-assign]
    installed: list[str] = []
    manager = TokenManager(
        bootstrap_token=bootstrap,
        api_tokens_api=api,  # type: ignore[arg-type]
        set_api_token=installed.append,
        token_dir=tmp_path,
        refresh_interval=timedelta(days=30),
    )
    try:
        assert manager.working_token == bootstrap
        assert installed[-1] == bootstrap
        assert manager._refresh_enabled is False  # pylint: disable=protected-access
        assert manager._thread is None  # pylint: disable=protected-access
    finally:
        manager.close()
