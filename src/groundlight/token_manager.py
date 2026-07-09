"""Client-side API token auto-refresh.

The Groundlight SDK treats the token supplied via ``GROUNDLIGHT_API_TOKEN`` (or
the ``api_token=`` argument) as a *bootstrap* credential. Instead of using it
directly for every API call, the SDK mints a short-lived token, caches it on
disk, and rotates it on a background thread. This limits the blast radius of a
leaked token and lets the server enforce a bounded token TTL without breaking
long-running integrations.

Design details live in the GL-1709 plan; the short version:

- One slot file per bootstrap token, keyed by the bootstrap token's raw-key
  snippet, at ``~/.groundlight/tokens/<snippet>.json`` (mode 0600).
- The slot stores the ``current`` working token plus a ``previous`` entry used
  for delayed cleanup.
- Coordination across processes sharing the slot uses an OS advisory lock on a
  sibling ``.lock`` file; the slot itself is written atomically (temp + rename).
- A per-instance daemon thread rotates the token once per day and deletes the
  previous token after a grace window so tokens do not accumulate.
"""

import datetime
import json
import logging
import os
import re
import secrets
import threading
from pathlib import Path
from typing import Callable, Optional

from filelock import FileLock, Timeout
from groundlight_openapi_client.api.api_tokens_api import ApiTokensApi
from groundlight_openapi_client.exceptions import NotFoundException
from groundlight_openapi_client.model.api_token_request import ApiTokenRequest

from groundlight.config import (
    CLEANUP_GRACE_FACTOR,
    DEFAULT_TOKEN_DIR,
    REFRESH_INTERVAL_DAYS,
    TOKEN_DIR_VARIABLE_NAME,
    TOKEN_TTL_DAYS,
)

logger = logging.getLogger("groundlight.sdk")

# The server exposes the first 20 characters of a raw key as its snippet.
RAW_KEY_SNIPPET_LENGTH = 20

# The name column is capped at 64 chars. A suffix is " " + 6 hex chars = 7 chars.
MAX_TOKEN_NAME_LENGTH = 64
NAME_SUFFIX_HEX_BYTES = 3  # secrets.token_hex(3) -> 6 hex characters
MAX_BASE_NAME_LENGTH = MAX_TOKEN_NAME_LENGTH - (NAME_SUFFIX_HEX_BYTES * 2) - 1

# Name given to auto-minted tokens when the base name cannot be determined.
FALLBACK_BASE_NAME = "sdk-auto"

# Matches a trailing " <6-hex>" suffix so rotation appends to the base name
# rather than growing the name on every rotation.
_SUFFIX_RE = re.compile(r" [0-9a-f]{6}$")

# How long to wait for the advisory lock before giving up on a refresh cycle.
# The on-disk token is valid for weeks, so a missed cycle is harmless.
LOCK_TIMEOUT_SECONDS = 10.0

# Backoff after a failed rotation. Without it, an overdue-but-failing rotation
# would busy-loop (the token stays "due", so the next wait is 0s) and hammer the
# API. The token is valid for weeks, so retrying every few minutes is plenty.
REFRESH_RETRY_BACKOFF_SECONDS = 300.0

TokenApiFactory = Callable[[str], ApiTokensApi]


def snippet_of(raw_key: str) -> str:
    """Return the snippet (first 20 chars) the server would store for a raw key."""
    return raw_key[:RAW_KEY_SNIPPET_LENGTH]


def _utcnow() -> datetime.datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.datetime.now(datetime.timezone.utc)


def _parse_dt(value: Optional[str]) -> Optional[datetime.datetime]:
    """Parse an ISO8601 string into a timezone-aware UTC datetime, or None."""
    if value is None:
        return None
    parsed = datetime.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed


def _format_dt(value: datetime.datetime) -> str:
    """Format a datetime as an ISO8601 UTC string."""
    return value.astimezone(datetime.timezone.utc).isoformat()


def derive_new_token_name(base_name: Optional[str]) -> str:
    """Build a unique token name from a base name plus a random 6-char hex suffix.

    Any existing suffix on the base name is stripped first so names do not grow
    on each rotation. When no base name is available, a generic name is used.
    """
    base = base_name if base_name else FALLBACK_BASE_NAME
    base = _SUFFIX_RE.sub("", base).strip()
    if not base:
        base = FALLBACK_BASE_NAME
    base = base[:MAX_BASE_NAME_LENGTH].rstrip()
    return f"{base} {secrets.token_hex(NAME_SUFFIX_HEX_BYTES)}"


class TokenManager:  # pylint: disable=too-many-instance-attributes
    """Owns the disk-cached working token for one bootstrap token and rotates it.

    The manager is constructed with the bootstrap token and two callbacks: a
    factory that builds an authenticated ``ApiTokensApi`` for a given token, and
    a setter that pushes a newly minted token into the live client so subsequent
    API calls use it. Callers should invoke :meth:`get_working_token` once at
    startup, then :meth:`start` the background refresh thread.
    """

    def __init__(
        self,
        *,
        bootstrap_token: str,
        token_api_factory: TokenApiFactory,
        set_active_token: Callable[[str], None],
        token_dir: Optional[str] = None,
    ):
        """Initialize a token manager for a single bootstrap token and its slot file."""
        self._bootstrap_token = bootstrap_token
        self._bootstrap_snippet = snippet_of(bootstrap_token)
        self._token_api_factory = token_api_factory
        self._set_active_token = set_active_token

        self._token_dir = Path(os.environ.get(TOKEN_DIR_VARIABLE_NAME) or token_dir or DEFAULT_TOKEN_DIR).expanduser()
        self._slot_path = self._token_dir / f"{self._bootstrap_snippet}.json"
        self._lock_path = self._token_dir / f"{self._bootstrap_snippet}.lock"
        self._file_lock = FileLock(str(self._lock_path), timeout=LOCK_TIMEOUT_SECONDS)

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._ensure_token_dir()

    # ------------------------------------------------------------------
    # Public lifecycle
    # ------------------------------------------------------------------

    def get_working_token(self) -> str:
        """Return a valid working token, minting one from the bootstrap token if needed.

        Uses the cached token when present and unexpired; otherwise mints a fresh
        token under the file lock. Raises if minting fails, since there is no
        usable credential in that case.
        """
        slot = self._read_slot()
        current = slot.get("current") if slot else None
        if current and not self._is_expired(current):
            return current["raw_key"]
        return self._refresh(authorizing_token=self._bootstrap_token)

    def start(self) -> None:
        """Start the background daemon thread that rotates the token once per day."""
        if self._thread is not None:
            return
        self._thread = threading.Thread(
            target=self._run,
            name=f"gl-token-refresh-{self._bootstrap_snippet[:8]}",
            daemon=True,
        )
        self._thread.start()

    def close(self) -> None:
        """Signal the refresh thread to stop and wait briefly for it to exit.

        Safe to call multiple times. Useful for tests and for web frameworks
        doing graceful shutdown; one-shot scripts can rely on the daemon thread
        being killed automatically at interpreter exit.
        """
        self._stop_event.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=LOCK_TIMEOUT_SECONDS)

    def remint_from_bootstrap(self) -> str:
        """Mint a fresh token authorized by the bootstrap token and make it active.

        Used as the fallback when a cached token is rejected with a 401 (for
        example, revoked server-side before its expiry). Forces a mint because the
        cached token looks valid locally but the server has rejected it.
        """
        return self._refresh(authorizing_token=self._bootstrap_token, force=True)

    # ------------------------------------------------------------------
    # Background thread
    # ------------------------------------------------------------------

    def _run(self) -> None:
        """Refresh loop body: wait until the token is due for rotation, then rotate.

        The wait is interruptible via the stop event, and every mint is
        deduplicated across processes by re-reading the slot under the lock.
        Exceptions during rotation are logged but never kill the thread, because
        the current token remains valid for weeks.
        """
        while not self._stop_event.is_set():
            wait_seconds = self._seconds_until_due()
            if self._stop_event.wait(timeout=wait_seconds):
                return
            try:
                self._rotate_if_due()
            except Exception:  # pylint: disable=broad-exception-caught
                # A transient failure (network, API, or filesystem) must not kill the
                # refresh thread: the current token stays valid for weeks, so we log
                # and retry after a backoff. The backoff matters because a failed
                # rotation leaves the token overdue, so the next wait would be 0s and
                # the loop would otherwise spin and hammer the API.
                logger.warning(
                    "Background API token refresh failed; retrying in %ss.",
                    REFRESH_RETRY_BACKOFF_SECONDS,
                    exc_info=True,
                )
                if self._stop_event.wait(timeout=REFRESH_RETRY_BACKOFF_SECONDS):
                    return

    def _seconds_until_due(self) -> float:
        """Return seconds until the current token is due for rotation (0 if overdue)."""
        slot = self._read_slot()
        current = slot.get("current") if slot else None
        if not current:
            return 0.0
        minted_at = _parse_dt(current.get("minted_at"))
        if minted_at is None:
            return 0.0
        interval = datetime.timedelta(days=REFRESH_INTERVAL_DAYS)
        due_at = minted_at + interval
        return max(0.0, (due_at - _utcnow()).total_seconds())

    def _rotate_if_due(self) -> None:
        """Rotate the token if it is due, authorizing the mint with the current token."""
        slot = self._read_slot()
        current = slot.get("current") if slot else None
        if current and not self._is_due_for_rotation(current):
            return
        authorizing_token = current["raw_key"] if current else self._bootstrap_token
        self._refresh(authorizing_token=authorizing_token)

    # ------------------------------------------------------------------
    # Core refresh (under the file lock)
    # ------------------------------------------------------------------

    def _refresh(self, *, authorizing_token: str, force: bool = False) -> str:
        """Clean up the previous token, mint a new one, and persist it, all under the lock.

        Returns the raw key of the token now in use. When ``force`` is False and
        the on-disk token is still valid (another process refreshed while we
        waited for the lock), that token is reused instead of minting again.
        ``force`` is used by the 401 fallback, where the cached token is known bad
        despite looking valid locally. If the lock cannot be acquired in time,
        falls back to the on-disk token when one is valid, since a missed cycle is
        harmless.
        """
        try:
            with self._file_lock:
                slot = self._read_slot() or {}
                current = slot.get("current")

                # Double-checked: another process may have refreshed while we waited.
                if not force and current and not self._is_expired(current) and not self._is_due_for_rotation(current):
                    self._set_active_token(current["raw_key"])
                    return current["raw_key"]

                api = self._token_api_factory(authorizing_token)
                self._cleanup_previous(api, slot.get("previous"))

                base_name = self._lookup_token_name(api, snippet_of(authorizing_token))
                new_current = self._mint(api, base_name)

                previous = None
                if current:
                    previous = {"name": current["name"], "minted_at": current["minted_at"]}
                self._write_slot({"current": new_current, "previous": previous})
                self._set_active_token(new_current["raw_key"])
                return new_current["raw_key"]
        except Timeout:
            disk_slot = self._read_slot()
            current = disk_slot.get("current") if disk_slot else None
            if current and not self._is_expired(current):
                self._set_active_token(current["raw_key"])
                return current["raw_key"]
            raise

    def _mint(self, api: ApiTokensApi, base_name: Optional[str]) -> dict:
        """Mint a new token via the API and return its slot ``current`` record."""
        new_name = derive_new_token_name(base_name)
        expires_at = _utcnow() + datetime.timedelta(days=TOKEN_TTL_DAYS)
        response = api.create_api_token(ApiTokenRequest(name=new_name, expires_at=expires_at))
        raw_key = response.raw_key
        return {
            "raw_key": raw_key,
            "snippet": snippet_of(raw_key),
            "name": new_name,
            "expires_at": _format_dt(expires_at),
            "minted_at": _format_dt(_utcnow()),
        }

    def _cleanup_previous(self, api: ApiTokensApi, previous: Optional[dict]) -> None:
        """Delete the previous token once it is older than the grace window.

        A 404 means the token is already gone, which is not an error. Runs under
        the lock so two processes never race to delete the same token.
        """
        if not previous:
            return
        minted_at = _parse_dt(previous.get("minted_at"))
        if minted_at is None:
            return
        grace = datetime.timedelta(days=CLEANUP_GRACE_FACTOR * REFRESH_INTERVAL_DAYS)
        if _utcnow() - minted_at < grace:
            return
        try:
            api.delete_api_token(previous["name"])
        except NotFoundException:
            logger.debug("Previous API token %r already deleted.", previous["name"])

    def _lookup_token_name(self, api: ApiTokensApi, snippet: str) -> Optional[str]:
        """Find the name of the token with the given snippet, or None if not found.

        TODO(GL-1709): Replace this paginated list-and-match with the dedicated
        ``get_api_token_by_snippet`` endpoint (see :meth:`_get_token_name_by_snippet`)
        before merging. That endpoint is not live in production yet, so for now we
        page through the caller's tokens and match on ``raw_key_snippet``.
        """
        page = 1
        while True:
            result = api.list_api_tokens(page=page)
            for token in result.results:
                if token.raw_key_snippet == snippet:
                    return token.name
            if getattr(result, "next", None) in (None, ""):
                return None
            page += 1

    def _get_token_name_by_snippet(self, api: ApiTokensApi, snippet: str) -> Optional[str]:
        """Find a token's name via the dedicated by-snippet endpoint.

        TODO(GL-1709): This is the intended replacement for
        :meth:`_lookup_token_name`, but it is NOT called yet because the
        ``GET /v1/api-tokens/by-snippet/{snippet}`` endpoint is not live in
        production. Switch :meth:`_refresh` to call this (and delete the
        list-and-match path) once the server-side endpoint is deployed.
        """
        try:
            token = api.get_api_token_by_snippet(snippet)
        except NotFoundException:
            return None
        return token.name

    # ------------------------------------------------------------------
    # Slot file IO
    # ------------------------------------------------------------------

    def _ensure_token_dir(self) -> None:
        """Create the token directory with private (0700) permissions if missing."""
        self._token_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    def _read_slot(self) -> Optional[dict]:
        """Read and parse the slot file, or return None if it does not exist."""
        try:
            with open(self._slot_path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def _write_slot(self, slot: dict) -> None:
        """Atomically write the slot file with private (0600) permissions."""
        tmp_path = self._slot_path.with_suffix(f".{os.getpid()}.tmp")
        fd = os.open(str(tmp_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(slot, f)
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise
        os.replace(str(tmp_path), str(self._slot_path))

    # ------------------------------------------------------------------
    # Small helpers
    # ------------------------------------------------------------------

    def _is_expired(self, current: dict) -> bool:
        """Return True if the given ``current`` record has passed its expiry."""
        expires_at = _parse_dt(current.get("expires_at"))
        if expires_at is None:
            return False
        return _utcnow() >= expires_at

    def _is_due_for_rotation(self, current: dict) -> bool:
        """Return True if the given ``current`` record is old enough to rotate."""
        minted_at = _parse_dt(current.get("minted_at"))
        if minted_at is None:
            return True
        return _utcnow() - minted_at >= datetime.timedelta(days=REFRESH_INTERVAL_DAYS)
