"""Background auto-refresh of the API token used by the Groundlight client.

The client is given a long-lived *bootstrap* token (from the ``api_token`` argument
or the ``GROUNDLIGHT_API_TOKEN`` env var). That token is used only to mint short-lived
working tokens; it is never used directly for API calls once a working token exists.

Each distinct bootstrap token gets its own on-disk cache slot keyed by its snippet, so
multiple credentials on one machine rotate independently. A per-instance daemon thread
mints a fresh working token daily and cleans up the previous one after a grace window.
Coordination across processes sharing the slot is handled by an OS advisory file lock
plus atomic slot writes, so exactly one process mints per cycle.

See the GL-1709 API Token Security Plan for the full design.
"""

import json
import logging
import os
import secrets
import sys
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import platformdirs
from filelock import FileLock, Timeout
from groundlight_openapi_client.exceptions import NotFoundException, UnauthorizedException
from groundlight_openapi_client.model.api_token_request import ApiTokenRequest

logger = logging.getLogger("groundlight.sdk")

# Token lifetimes and cadence. Defined as constants so they are easy to change later.
TOKEN_TTL_DAYS = 30  # working tokens are minted with this expiry
REFRESH_INTERVAL_DAYS = 1  # mint a fresh working token this often
CLEANUP_GRACE_FACTOR = 2  # delete the previous token after this many refresh intervals

SNIPPET_LENGTH = 20  # first N chars of a raw key; also the per-token cache slot key
TOKEN_NAME_MAX_LENGTH = 64  # server-side cap on the token name column
RANDOM_SUFFIX_LENGTH = 6  # hex chars appended to a minted token's name
FALLBACK_TOKEN_NAME = "sdk-auto"  # base name used when the current token can't be found

MINT_REQUEST_TIMEOUT = 10.0  # seconds; bounds each token API call so a hang can't pin the lock
LOCK_ACQUIRE_TIMEOUT = 5.0  # seconds; a missed refresh cycle is harmless, so don't block forever

_SECONDS_PER_DAY = 24 * 60 * 60


class TokenRefreshError(Exception):
    """Raised when the client cannot obtain a working token at startup."""


def resolve_token_dir() -> Path:
    """Return the directory where token cache slots are stored.

    Defaults to ``~/.groundlight/tokens`` (a platform-appropriate app-data dir on
    Windows), overridable via the ``GROUNDLIGHT_TOKEN_DIR`` env var.
    """
    override = os.environ.get("GROUNDLIGHT_TOKEN_DIR")
    if override:
        return Path(override).expanduser()
    if sys.platform.startswith("win"):
        return Path(platformdirs.user_data_dir("groundlight")) / "tokens"
    return Path.home() / ".groundlight" / "tokens"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _to_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _from_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _coerce_dt(value, default: datetime) -> datetime:
    """Normalize an expires_at value (datetime or ISO string) to an aware UTC datetime."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str) and value:
        try:
            return _from_iso(value)
        except ValueError:
            return default
    return default


class TokenRefresher:  # pylint: disable=too-many-instance-attributes
    """Owns the working-token lifecycle for a single Groundlight client instance.

    Bootstraps a working token from the disk cache or by minting, keeps the client's
    active token up to date on ``configuration``, and runs a daemon thread that rotates
    the token on a daily cadence.
    """

    def __init__(self, tokens_api, configuration, bootstrap_token: str, token_dir: Optional[Path] = None):
        self._tokens_api = tokens_api
        self._configuration = configuration
        self._bootstrap_token = bootstrap_token
        self._snippet = bootstrap_token[:SNIPPET_LENGTH]

        self._token_dir = token_dir or resolve_token_dir()
        self._slot_path = self._token_dir / f"{self._snippet}.json"
        # The lock file is a stable sibling of the slot file. It is never renamed, so its
        # inode is constant even as the slot file is atomically replaced -- this is what
        # keeps the advisory lock meaningful across refreshes.
        self._lock = FileLock(str(self._token_dir / f"{self._snippet}.lock"))

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        # Disabled if the token endpoints aren't deployed yet; see bootstrap().
        self._enabled = True

    # -- lifecycle ---------------------------------------------------------------

    def bootstrap(self) -> None:
        """Set the client's active token to a valid working token, minting one if needed.

        Uses a cached token when present and unexpired; otherwise mints a new one under
        the file lock. Raises TokenRefreshError if the bootstrap token is rejected.

        TODO(GL-1618): The token endpoints (zuuul PR #6560) are not yet deployed
        everywhere. Until they are, a 404 means "server side not live yet": we keep using
        the bootstrap token directly and skip rotation, so the SDK keeps working during
        the staged rollout. Remove this graceful-degradation path once the endpoints are
        deployed to all environments and the SDK is enabled per the GL-1709 merge plan.
        """
        self._ensure_token_dir()

        cached = self._load_current()
        if cached and not self._is_expired(cached):
            self._set_active_token(cached["raw_key"])
            return

        try:
            with self._lock.acquire(timeout=LOCK_ACQUIRE_TIMEOUT):
                # Re-check under the lock: another process may have minted while we waited.
                cached = self._load_current()
                if cached and not self._is_expired(cached):
                    self._set_active_token(cached["raw_key"])
                    return
                self._refresh(previous_current=cached)
        except Timeout as exc:
            # Someone else holds the lock, likely mid-mint. Re-read what they wrote.
            cached = self._load_current()
            if cached and not self._is_expired(cached):
                self._set_active_token(cached["raw_key"])
                return
            raise TokenRefreshError("Timed out acquiring the token lock and no valid cached token was found.") from exc
        except NotFoundException:
            self._enabled = False
            self._set_active_token(self._bootstrap_token)
            logger.info(
                "API token endpoints are not available at this endpoint; skipping token auto-refresh "
                "and using the provided token directly."
            )
        except UnauthorizedException as e:
            raise TokenRefreshError(
                "The provided API token was rejected while minting a working token. It is probably invalid or revoked."
            ) from e
        except TokenRefreshError:
            raise
        except Exception as e:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            # Bootstrap must surface any mint failure clearly rather than silently continuing.
            raise TokenRefreshError(f"Failed to mint an initial API token: {e}") from e

    def start(self) -> None:
        """Start the background daemon thread that rotates the working token, if enabled."""
        if not self._enabled:
            return
        self._thread = threading.Thread(
            target=self._run,
            name=f"gl-token-refresh-{self._snippet[:8]}",
            daemon=True,
        )
        self._thread.start()

    def close(self, timeout: float = 5.0) -> None:
        """Signal the refresh thread to stop and wait briefly for it to exit."""
        self._stop_event.set()
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=timeout)

    # -- background loop ---------------------------------------------------------

    def _run(self) -> None:
        while not self._stop_event.is_set():
            current = self._load_current()
            wait_seconds = self._seconds_until_refresh(current)
            # Interruptible sleep: close() sets the event and wakes us immediately.
            if self._stop_event.wait(timeout=wait_seconds):
                return
            try:
                self._refresh_cycle()
            except Exception as e:  # noqa: BLE001  # pylint: disable=broad-exception-caught
                # A failed cycle must not kill the thread; the current token is still valid.
                logger.warning(f"Token refresh cycle failed; will retry next cycle: {e}", exc_info=True)

    def _refresh_cycle(self) -> None:
        """Acquire the lock, and mint + clean up only if no other process beat us to it."""
        try:
            with self._lock.acquire(timeout=LOCK_ACQUIRE_TIMEOUT):
                current = self._load_current()
                if current and self._age_seconds(current) < REFRESH_INTERVAL_DAYS * _SECONDS_PER_DAY:
                    # Another process already refreshed within this interval; just adopt it.
                    self._set_active_token(current["raw_key"])
                    return
                self._cleanup_previous()
                self._refresh(previous_current=current)
        except Timeout:
            logger.debug("Skipping token refresh cycle: could not acquire lock (another process is refreshing).")

    # -- minting and cleanup (all called while holding the lock) ------------------

    def _refresh(self, previous_current: Optional[dict]) -> None:
        """Mint a new working token, persist it as current, and demote the old one.

        Both the name lookup and the mint use the currently active token. If that token
        was revoked server-side (401 on either call), fall back once to the bootstrap
        token and retry the whole sequence before giving up.
        """
        try:
            new_current = self._lookup_and_mint()
        except UnauthorizedException:
            logger.info("Active token rejected during refresh; retrying with the bootstrap token.")
            self._set_active_token(self._bootstrap_token)
            new_current = self._lookup_and_mint()

        previous = None
        if previous_current:
            previous = {"name": previous_current["name"], "minted_at": previous_current["minted_at"]}
        self._write_slot(current=new_current, previous=previous)
        self._set_active_token(new_current["raw_key"])

    def _lookup_and_mint(self) -> dict:
        """Find the active token's name (for a readable new name) and mint its replacement."""
        base_name = self._lookup_current_name() or FALLBACK_TOKEN_NAME
        return self._mint(self._generate_token_name(base_name))

    def _mint(self, name: str) -> dict:
        """Create a new API token and return its slot representation."""
        expires_at = _utcnow() + timedelta(days=TOKEN_TTL_DAYS)
        request = ApiTokenRequest(name=name, expires_at=expires_at)
        response = self._tokens_api.create_api_token(request, _request_timeout=MINT_REQUEST_TIMEOUT)

        data = response.to_dict()
        minted_at = _utcnow()
        return {
            "raw_key": data["raw_key"],
            "snippet": data.get("raw_key_snippet", data["raw_key"][:SNIPPET_LENGTH]),
            "name": data["name"],
            "expires_at": _to_iso(_coerce_dt(data.get("expires_at"), minted_at + timedelta(days=TOKEN_TTL_DAYS))),
            "minted_at": _to_iso(minted_at),
        }

    def _cleanup_previous(self) -> None:
        """Delete the previous token once it is safely past the grace window."""
        slot = self._read_slot()
        previous = slot.get("previous")
        if not previous:
            return
        age = (_utcnow() - _from_iso(previous["minted_at"])).total_seconds()
        if age < CLEANUP_GRACE_FACTOR * REFRESH_INTERVAL_DAYS * _SECONDS_PER_DAY:
            return
        try:
            self._tokens_api.delete_api_token(previous["name"], _request_timeout=MINT_REQUEST_TIMEOUT)
        except NotFoundException:
            pass  # already gone; nothing to do
        # Clear previous so we don't attempt the delete again next cycle.
        self._write_slot(current=slot.get("current"), previous=None)

    def _lookup_current_name(self) -> Optional[str]:
        """Find the active token's name by scanning the paginated token list.

        TODO(GL-1618): This paginated scan is temporary. Once
        GET /v1/api-tokens/by-snippet/<snippet> is deployed (zuuul PR #6579), replace
        this with _lookup_name_by_snippet(), which is a single direct lookup. Switch
        before merging the server change.
        """
        active_token = self._configuration.api_key["ApiToken"]
        page = 1
        while True:
            response = self._tokens_api.list_api_tokens(page=page, _request_timeout=MINT_REQUEST_TIMEOUT)
            data = response.to_dict()
            for token in data.get("results", []):
                snippet = token.get("raw_key_snippet")
                if snippet and active_token.startswith(snippet):
                    return token.get("name")
            if not data.get("next"):
                return None
            page += 1

    def _lookup_name_by_snippet(self) -> Optional[str]:
        """Find the active token's name via the direct by-snippet endpoint.

        TODO(GL-1618): Not called yet. The GET /v1/api-tokens/by-snippet/<snippet>
        endpoint (zuuul PR #6579) is not live. Once it is deployed, call this from
        _refresh() in place of _lookup_current_name(), then delete the paginated scan.
        """
        snippet = self._configuration.api_key["ApiToken"][:SNIPPET_LENGTH]
        try:
            response = self._tokens_api.get_api_token_by_snippet(snippet, _request_timeout=MINT_REQUEST_TIMEOUT)
        except NotFoundException:
            return None
        return response.to_dict().get("name")

    def _generate_token_name(self, base_name: str) -> str:
        """Append a random hex suffix to base_name, truncating to fit the name column."""
        suffix = secrets.token_hex(RANDOM_SUFFIX_LENGTH // 2)
        max_base = TOKEN_NAME_MAX_LENGTH - len(suffix) - 1  # 1 for the separating space
        return f"{base_name[:max_base]} {suffix}"

    # -- slot file I/O -----------------------------------------------------------

    def _ensure_token_dir(self) -> None:
        try:
            self._token_dir.mkdir(parents=True, exist_ok=True)
            os.chmod(self._token_dir, 0o700)
        except OSError as e:
            raise TokenRefreshError(
                f"Cannot use token cache directory {self._token_dir}: {e}. "
                "Set GROUNDLIGHT_TOKEN_DIR to a writable location."
            ) from e

    def _read_slot(self) -> dict:
        try:
            with open(self._slot_path, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _load_current(self) -> Optional[dict]:
        return self._read_slot().get("current")

    def _write_slot(self, current: Optional[dict], previous: Optional[dict]) -> None:
        """Atomically write the slot file (temp file + rename) with 0600 permissions."""
        payload = json.dumps({"current": current, "previous": previous}, indent=2)
        tmp_path = self._slot_path.with_suffix(f".{os.getpid()}.tmp")
        fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(payload)
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise
        os.replace(tmp_path, self._slot_path)

    # -- helpers -----------------------------------------------------------------

    def _set_active_token(self, raw_key: str) -> None:
        self._configuration.api_key["ApiToken"] = raw_key

    def _is_expired(self, current: dict) -> bool:
        return _utcnow() >= _from_iso(current["expires_at"])

    def _age_seconds(self, current: dict) -> float:
        return (_utcnow() - _from_iso(current["minted_at"])).total_seconds()

    def _seconds_until_refresh(self, current: Optional[dict]) -> float:
        if not current:
            return 0.0
        remaining = REFRESH_INTERVAL_DAYS * _SECONDS_PER_DAY - self._age_seconds(current)
        return max(0.0, remaining)
