"""Unit tests for the client-side API token auto-refresh (token_manager.py).

These tests never touch the network: a fake ApiTokensApi records mint/list/delete
calls, and the slot directory is a pytest tmp_path.
"""

import datetime
import json
import stat
import sys

import pytest
from groundlight.token_manager import (
    CLEANUP_GRACE_FACTOR,
    MAX_TOKEN_NAME_LENGTH,
    NAME_SUFFIX_HEX_BYTES,
    REFRESH_INTERVAL_DAYS,
    TOKEN_TTL_DAYS,
    TokenManager,
    derive_new_token_name,
    snippet_of,
)
from groundlight_openapi_client.exceptions import NotFoundException

BOOTSTRAP_TOKEN = "api_2BootstrapKeyABCDEFGHIJ"
BOOTSTRAP_SNIPPET = snippet_of(BOOTSTRAP_TOKEN)
SUFFIX_HEX_LEN = NAME_SUFFIX_HEX_BYTES * 2
PRIVATE_FILE_MODE = 0o600


class FakeToken:
    """A minimal stand-in for a server ApiToken/list entry."""

    def __init__(self, name, raw_key_snippet):
        self.name = name
        self.raw_key_snippet = raw_key_snippet


class FakeCreateResponse:
    """A minimal stand-in for ApiTokenCreateResponse (only raw_key is read)."""

    def __init__(self, raw_key):
        self.raw_key = raw_key


class FakePage:
    """A minimal stand-in for a page of PaginatedApiTokenList."""

    def __init__(self, results, next_url=None):
        self.results = results
        self.next = next_url


class FakeApiTokensApi:
    """In-memory fake of ApiTokensApi that records calls for assertions."""

    def __init__(self):
        self.existing = []  # list of FakeToken visible via list_api_tokens
        self.created = []  # names passed to create_api_token
        self.deleted = []  # names passed to delete_api_token
        self.mint_counter = 0
        self.raise_not_found_on_delete = False

    def create_api_token(self, request):
        """Record the requested name and return a fresh unique raw key."""
        self.mint_counter += 1
        self.created.append(request.name)
        raw_key = f"api_MINTED{self.mint_counter:04d}{'Z' * 12}"
        self.existing.append(FakeToken(name=request.name, raw_key_snippet=snippet_of(raw_key)))
        return FakeCreateResponse(raw_key=raw_key)

    def list_api_tokens(self, page=1):
        """Return all existing tokens on a single page."""
        return FakePage(results=list(self.existing))

    def delete_api_token(self, name):
        """Record a delete, optionally simulating an already-deleted token."""
        self.deleted.append(name)
        if self.raise_not_found_on_delete:
            raise NotFoundException(status=404, reason="Not Found")

    def get_api_token_by_snippet(self, snippet):
        """Return the token matching the snippet, or raise NotFound."""
        for token in self.existing:
            if token.raw_key_snippet == snippet:
                return token
        raise NotFoundException(status=404, reason="Not Found")


def make_manager(tmp_path, fake_api, *, bootstrap_token=BOOTSTRAP_TOKEN):
    """Build a TokenManager wired to the fake API and a temp slot directory."""
    active = {"token": None}

    def factory(_token):
        return fake_api

    def set_active(token):
        active["token"] = token

    manager = TokenManager(
        bootstrap_token=bootstrap_token,
        token_api_factory=factory,
        set_active_token=set_active,
        token_dir=str(tmp_path),
    )
    return manager, active


def read_slot(manager):
    """Read the raw slot dict from disk for assertions."""
    with open(manager._slot_path, encoding="utf-8") as f:  # noqa: SLF001
        return json.load(f)


# --------------------------------------------------------------------------
# Naming helpers
# --------------------------------------------------------------------------


def test_snippet_of_takes_first_20_chars():
    assert snippet_of("api_" + "x" * 40) == ("api_" + "x" * 16)


def test_derive_name_appends_suffix():
    name = derive_new_token_name("My Token")
    assert name.startswith("My Token ")
    assert len(name.rsplit(" ", 1)[1]) == SUFFIX_HEX_LEN


def test_derive_name_strips_existing_suffix_so_names_do_not_grow():
    name = derive_new_token_name("My Token a7f3c2")
    base, suffix = name.rsplit(" ", 1)
    assert base == "My Token"
    assert len(suffix) == SUFFIX_HEX_LEN


def test_derive_name_uses_fallback_when_missing():
    assert derive_new_token_name(None).startswith("sdk-auto ")
    assert derive_new_token_name("").startswith("sdk-auto ")


def test_derive_name_truncates_to_64_chars():
    name = derive_new_token_name("z" * 200)
    assert len(name) == MAX_TOKEN_NAME_LENGTH


# --------------------------------------------------------------------------
# Cold start / caching
# --------------------------------------------------------------------------


def test_cold_start_mints_and_writes_slot(tmp_path):
    fake = FakeApiTokensApi()
    fake.existing.append(FakeToken(name="My Token", raw_key_snippet=BOOTSTRAP_SNIPPET))
    manager, active = make_manager(tmp_path, fake)

    mints_before = fake.mint_counter
    token = manager.get_working_token()

    assert token.startswith("api_MINTED")
    assert active["token"] == token
    assert fake.mint_counter == mints_before + 1
    slot = read_slot(manager)
    assert slot["current"]["raw_key"] == token
    assert slot["current"]["name"].startswith("My Token ")
    assert slot["previous"] is None


def test_cold_start_uses_fallback_name_when_snippet_absent(tmp_path):
    fake = FakeApiTokensApi()  # bootstrap token not present in list
    manager, _ = make_manager(tmp_path, fake)

    manager.get_working_token()

    assert fake.created[0].startswith("sdk-auto ")


def test_cached_valid_token_is_reused_without_minting(tmp_path):
    fake = FakeApiTokensApi()
    fake.existing.append(FakeToken(name="My Token", raw_key_snippet=BOOTSTRAP_SNIPPET))
    manager, _ = make_manager(tmp_path, fake)

    first = manager.get_working_token()
    mints_after_first = fake.mint_counter
    second = manager.get_working_token()

    assert first == second
    assert fake.mint_counter == mints_after_first


def test_expired_cached_token_triggers_mint(tmp_path):
    fake = FakeApiTokensApi()
    fake.existing.append(FakeToken(name="My Token", raw_key_snippet=BOOTSTRAP_SNIPPET))
    manager, _ = make_manager(tmp_path, fake)
    manager.get_working_token()
    mints_before = fake.mint_counter

    # Force the cached token to be expired.
    slot = read_slot(manager)
    slot["current"]["expires_at"] = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
    ).isoformat()
    manager._write_slot(slot)  # noqa: SLF001

    manager.get_working_token()
    assert fake.mint_counter == mints_before + 1


def test_slot_file_is_private(tmp_path):
    fake = FakeApiTokensApi()
    manager, _ = make_manager(tmp_path, fake)
    manager.get_working_token()

    mode = stat.S_IMODE(manager._slot_path.stat().st_mode)  # noqa: SLF001
    assert mode == PRIVATE_FILE_MODE


# --------------------------------------------------------------------------
# Rotation
# --------------------------------------------------------------------------


def _age_current_token(manager, days):
    """Backdate the current token's minted_at by the given number of days."""
    slot = read_slot(manager)
    slot["current"]["minted_at"] = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
    ).isoformat()
    manager._write_slot(slot)  # noqa: SLF001


def test_rotate_not_due_is_noop(tmp_path):
    fake = FakeApiTokensApi()
    fake.existing.append(FakeToken(name="My Token", raw_key_snippet=BOOTSTRAP_SNIPPET))
    manager, _ = make_manager(tmp_path, fake)
    manager.get_working_token()
    mints_before = fake.mint_counter

    manager._rotate_if_due()  # noqa: SLF001
    assert fake.mint_counter == mints_before


def test_rotate_when_due_mints_and_demotes_previous(tmp_path):
    fake = FakeApiTokensApi()
    fake.existing.append(FakeToken(name="My Token", raw_key_snippet=BOOTSTRAP_SNIPPET))
    manager, active = make_manager(tmp_path, fake)
    manager.get_working_token()
    first_slot = read_slot(manager)
    first_name = first_slot["current"]["name"]
    mints_before = fake.mint_counter

    _age_current_token(manager, REFRESH_INTERVAL_DAYS + 1)
    manager._rotate_if_due()  # noqa: SLF001

    assert fake.mint_counter == mints_before + 1
    slot = read_slot(manager)
    assert slot["current"]["name"] != first_name
    assert slot["previous"]["name"] == first_name
    assert active["token"] == slot["current"]["raw_key"]


# --------------------------------------------------------------------------
# Cleanup of the previous token
# --------------------------------------------------------------------------


def test_previous_within_grace_is_not_deleted(tmp_path):
    fake = FakeApiTokensApi()
    fake.existing.append(FakeToken(name="My Token", raw_key_snippet=BOOTSTRAP_SNIPPET))
    manager, _ = make_manager(tmp_path, fake)
    manager.get_working_token()

    _age_current_token(manager, REFRESH_INTERVAL_DAYS + 1)
    manager._rotate_if_due()  # noqa: SLF001 - creates a fresh previous entry

    assert fake.deleted == []


def test_previous_past_grace_is_deleted(tmp_path):
    fake = FakeApiTokensApi()
    fake.existing.append(FakeToken(name="My Token", raw_key_snippet=BOOTSTRAP_SNIPPET))
    manager, _ = make_manager(tmp_path, fake)
    manager.get_working_token()

    # First rotation creates a previous entry, then backdate it past the grace window.
    _age_current_token(manager, REFRESH_INTERVAL_DAYS + 1)
    manager._rotate_if_due()  # noqa: SLF001
    slot = read_slot(manager)
    old_previous_name = slot["previous"]["name"]
    slot["previous"]["minted_at"] = (
        datetime.datetime.now(datetime.timezone.utc)
        - datetime.timedelta(days=CLEANUP_GRACE_FACTOR * REFRESH_INTERVAL_DAYS + 1)
    ).isoformat()
    # Also age the current token so the next rotation is due.
    slot["current"]["minted_at"] = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=REFRESH_INTERVAL_DAYS + 1)
    ).isoformat()
    manager._write_slot(slot)  # noqa: SLF001

    manager._rotate_if_due()  # noqa: SLF001
    assert old_previous_name in fake.deleted


def test_cleanup_tolerates_already_deleted_token(tmp_path):
    fake = FakeApiTokensApi()
    fake.raise_not_found_on_delete = True
    manager, _ = make_manager(tmp_path, fake)
    manager.get_working_token()

    manager._cleanup_previous(  # noqa: SLF001
        fake,
        {
            "name": "gone",
            "minted_at": (
                datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(days=CLEANUP_GRACE_FACTOR * REFRESH_INTERVAL_DAYS + 1)
            ).isoformat(),
        },
    )
    assert fake.deleted == ["gone"]


# --------------------------------------------------------------------------
# 401 fallback and the (not-yet-used) by-snippet lookup
# --------------------------------------------------------------------------


def test_remint_from_bootstrap_mints_new_token(tmp_path):
    fake = FakeApiTokensApi()
    fake.existing.append(FakeToken(name="My Token", raw_key_snippet=BOOTSTRAP_SNIPPET))
    manager, active = make_manager(tmp_path, fake)
    manager.get_working_token()
    mints_before = fake.mint_counter

    new_token = manager.remint_from_bootstrap()
    assert fake.mint_counter == mints_before + 1
    assert active["token"] == new_token


def test_get_token_name_by_snippet_uncalled_helper(tmp_path):
    fake = FakeApiTokensApi()
    fake.existing.append(FakeToken(name="Found It", raw_key_snippet="api_lookupsnippetxyz"))
    manager, _ = make_manager(tmp_path, fake)

    assert manager._get_token_name_by_snippet(fake, "api_lookupsnippetxyz") == "Found It"  # noqa: SLF001
    assert manager._get_token_name_by_snippet(fake, "api_missing") is None  # noqa: SLF001


# --------------------------------------------------------------------------
# TTL and scheduling
# --------------------------------------------------------------------------


def test_minted_expiry_is_ttl_days_out(tmp_path):
    fake = FakeApiTokensApi()
    manager, _ = make_manager(tmp_path, fake)
    manager.get_working_token()

    slot = read_slot(manager)
    minted = datetime.datetime.fromisoformat(slot["current"]["minted_at"])
    expires = datetime.datetime.fromisoformat(slot["current"]["expires_at"])
    assert abs((expires - minted).days - TOKEN_TTL_DAYS) <= 1


def test_seconds_until_due_is_zero_without_slot(tmp_path):
    fake = FakeApiTokensApi()
    manager, _ = make_manager(tmp_path, fake)
    assert manager._seconds_until_due() == 0.0  # noqa: SLF001


def test_seconds_until_due_positive_for_fresh_token(tmp_path):
    fake = FakeApiTokensApi()
    manager, _ = make_manager(tmp_path, fake)
    manager.get_working_token()
    assert manager._seconds_until_due() > 0.0  # noqa: SLF001


def test_run_loop_survives_and_backs_off_on_rotation_failure(tmp_path, monkeypatch):
    fake = FakeApiTokensApi()
    manager, _ = make_manager(tmp_path, fake)
    calls = {"n": 0}

    def boom():
        calls["n"] += 1
        manager._stop_event.set()  # noqa: SLF001 - exit the loop after one failure
        raise RuntimeError("mint failed")

    monkeypatch.setattr(manager, "_seconds_until_due", lambda: 0.0)  # noqa: SLF001
    monkeypatch.setattr(manager, "_rotate_if_due", boom)  # noqa: SLF001

    manager._run()  # noqa: SLF001 - must not raise, and must not spin

    assert calls["n"] == 1


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX file-mode assertion")
def test_token_dir_is_created_private(tmp_path):
    fake = FakeApiTokensApi()
    subdir = tmp_path / "nested" / "tokens"
    active = {"token": None}
    TokenManager(
        bootstrap_token=BOOTSTRAP_TOKEN,
        token_api_factory=lambda _t: fake,
        set_active_token=lambda t: active.update(token=t),
        token_dir=str(subdir),
    )
    assert subdir.exists()
