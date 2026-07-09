"""Disk-backed API token cache and background refresh for short-lived working tokens."""

from __future__ import annotations

import json
import logging
import os
import secrets
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from filelock import FileLock, Timeout
from groundlight_openapi_client.api.api_tokens_api import ApiTokensApi
from groundlight_openapi_client.exceptions import NotFoundException
from groundlight_openapi_client.model.api_token_request import ApiTokenRequest
from platformdirs import user_data_dir

from groundlight.config import TOKEN_DIR_VARIABLE_NAME

logger = logging.getLogger("groundlight.sdk")

TOKEN_TTL_DAYS = 30
REFRESH_INTERVAL_DAYS = 1
CLEANUP_GRACE_FACTOR = 2
SNIPPET_LENGTH = 20
NAME_MAX_LENGTH = 64
NAME_SUFFIX_CHARS = 7  # space + 6 hex chars
LOCK_TIMEOUT_SECONDS = 5
MINT_REQUEST_TIMEOUT_SECONDS = 10
FALLBACK_TOKEN_NAME_PREFIX = "sdk-auto"


@dataclass
class CachedToken:
    """One working token stored in a cache slot."""

    raw_key: str
    snippet: str
    name: str
    expires_at: datetime
    minted_at: datetime

    def to_dict(self) -> dict[str, str]:
        return {
            "raw_key": self.raw_key,
            "snippet": self.snippet,
            "name": self.name,
            "expires_at": _format_utc(self.expires_at),
            "minted_at": _format_utc(self.minted_at),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CachedToken":
        return cls(
            raw_key=data["raw_key"],
            snippet=data["snippet"],
            name=data["name"],
            expires_at=_parse_utc(data["expires_at"]),
            minted_at=_parse_utc(data["minted_at"]),
        )


@dataclass
class PreviousToken:
    """Metadata needed to delete a superseded token after the grace window."""

    name: str
    minted_at: datetime

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "minted_at": _format_utc(self.minted_at)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PreviousToken":
        return cls(name=data["name"], minted_at=_parse_utc(data["minted_at"]))


@dataclass
class TokenSlot:
    """On-disk cache slot for one bootstrap token."""

    current: CachedToken
    previous: Optional[PreviousToken] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "current": self.current.to_dict(),
            "previous": self.previous.to_dict() if self.previous else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TokenSlot":
        previous_data = data.get("previous")
        return cls(
            current=CachedToken.from_dict(data["current"]),
            previous=PreviousToken.from_dict(previous_data) if previous_data else None,
        )


def token_snippet(raw_key: str) -> str:
    """Return the cache-key snippet for a raw API token."""
    return raw_key[:SNIPPET_LENGTH]


def default_token_dir() -> Path:
    """Resolve the token cache directory from env or the platform user data dir."""
    override = os.environ.get(TOKEN_DIR_VARIABLE_NAME)
    if override:
        return Path(override).expanduser()
    return Path(user_data_dir("groundlight", appauthor=False)) / "tokens"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _format_utc(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_utc(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _next_token_name(base_name: Optional[str]) -> str:
    suffix = f" {secrets.token_hex(3)}"
    if not base_name:
        return f"{FALLBACK_TOKEN_NAME_PREFIX}{suffix}"
    max_base_len = NAME_MAX_LENGTH - NAME_SUFFIX_CHARS
    truncated = base_name[:max_base_len]
    return f"{truncated}{suffix}"


class TokenManager:  # pylint: disable=too-many-instance-attributes
    """Manages a short-lived working token backed by a per-bootstrap-token disk cache."""

    def __init__(  # noqa: PLR0913 # pylint: disable=too-many-arguments
        self,
        bootstrap_token: str,
        api_tokens_api: ApiTokensApi,
        set_api_token: Callable[[str], None],
        token_dir: Optional[Path] = None,
        refresh_interval: Optional[timedelta] = None,
        token_ttl: Optional[timedelta] = None,
    ):
        """Create a manager for one bootstrap token and start using a cached or freshly minted working token."""
        self.bootstrap_token = bootstrap_token
        self.bootstrap_snippet = token_snippet(bootstrap_token)
        self.api_tokens_api = api_tokens_api
        self._set_api_token = set_api_token
        self.token_dir = Path(token_dir) if token_dir is not None else default_token_dir()
        self.refresh_interval = refresh_interval or timedelta(days=REFRESH_INTERVAL_DAYS)
        self.token_ttl = token_ttl or timedelta(days=TOKEN_TTL_DAYS)
        self.cleanup_grace = self.refresh_interval * CLEANUP_GRACE_FACTOR

        self._slot_path = self.token_dir / f"{self.bootstrap_snippet}.json"
        self._lock_path = self.token_dir / f"{self.bootstrap_snippet}.lock"
        self._lock = FileLock(str(self._lock_path), timeout=LOCK_TIMEOUT_SECONDS)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._slot: Optional[TokenSlot] = None
        # False when the server does not expose api-tokens endpoints yet (e.g. older prod).
        self._refresh_enabled = True

        self._ensure_token_dir()
        self._initialize_working_token()
        if self._refresh_enabled:
            self._start_refresh_thread()

    @property
    def working_token(self) -> str:
        """Return the raw key currently used for API calls."""
        if self._slot is None:
            raise RuntimeError("TokenManager has no working token")
        return self._slot.current.raw_key

    def close(self) -> None:
        """Stop the background refresh thread."""
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2)

    def remint_after_unauthorized(self) -> bool:
        """Re-mint using the bootstrap token after a 401 on the cached working token.

        Returns True if a new working token was installed.
        """
        if not self._refresh_enabled:
            return False
        # Avoid deadlock if a mint/refresh already holds the lock and its HTTP call 401s.
        if self._lock.is_locked:
            return False
        previous_working = self._slot.current.raw_key if self._slot is not None else None
        try:
            with self._lock:
                self._mint_and_persist(auth_token=self.bootstrap_token, previous_slot=self._slot)
            return True
        except Timeout:
            logger.warning("Could not acquire token lock while recovering from 401; skipping remint")
            if previous_working is not None:
                self._set_api_token(previous_working)
            return False
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Failed to remint API token after 401")
            if previous_working is not None:
                self._set_api_token(previous_working)
            return False

    def _ensure_token_dir(self) -> None:
        try:
            self.token_dir.mkdir(parents=True, exist_ok=True)
            if os.name != "nt":
                os.chmod(self.token_dir, 0o700)
        except OSError as exc:
            raise RuntimeError(
                f"Unable to create token cache directory '{self.token_dir}'. "
                f"Set {TOKEN_DIR_VARIABLE_NAME} to a writable path."
            ) from exc

    def _initialize_working_token(self) -> None:
        try:
            with self._lock:
                slot = self._read_slot()
                if slot is not None and not self._is_expired(slot.current):
                    self._install_slot(slot)
                    return
                try:
                    self._mint_and_persist(auth_token=self.bootstrap_token, previous_slot=slot)
                except NotFoundException:
                    # api-tokens endpoints are not deployed on this server yet.
                    logger.warning(
                        "API token management endpoints are unavailable; "
                        "using the bootstrap token without auto-refresh."
                    )
                    self._use_bootstrap_only()
        except Timeout as exc:
            raise RuntimeError(
                f"Timed out acquiring token lock at '{self._lock_path}'. Another process may be stuck holding the lock."
            ) from exc

    def _use_bootstrap_only(self) -> None:
        """Fall back to the bootstrap token when short-lived token APIs are unavailable."""
        self._refresh_enabled = False
        now = _utcnow()
        self._slot = TokenSlot(
            current=CachedToken(
                raw_key=self.bootstrap_token,
                snippet=self.bootstrap_snippet,
                name="bootstrap",
                expires_at=now + self.token_ttl,
                minted_at=now,
            )
        )
        self._set_api_token(self.bootstrap_token)

    def _start_refresh_thread(self) -> None:
        thread_name = f"gl-token-refresh-{self.bootstrap_snippet[:8]}"
        self._thread = threading.Thread(target=self._refresh_loop, name=thread_name, daemon=True)
        self._thread.start()

    def _refresh_loop(self) -> None:
        while not self._stop_event.is_set():
            wait_seconds = self._seconds_until_refresh()
            if self._stop_event.wait(timeout=wait_seconds):
                return
            try:
                self._refresh_once()
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("API token refresh failed; will retry on the next cycle", exc_info=True)

    def _seconds_until_refresh(self) -> float:
        if self._slot is None:
            return 0.0
        due_at = self._slot.current.minted_at + self.refresh_interval
        return max(0.0, (due_at - _utcnow()).total_seconds())

    def _refresh_once(self) -> None:
        try:
            with self._lock:
                slot = self._read_slot() or self._slot
                if slot is None:
                    self._mint_and_persist(auth_token=self.bootstrap_token, previous_slot=None)
                    return
                if _utcnow() < slot.current.minted_at + self.refresh_interval:
                    self._install_slot(slot)
                    return
                self._cleanup_previous(slot)
                self._mint_and_persist(auth_token=slot.current.raw_key, previous_slot=slot)
        except Timeout:
            logger.warning("Could not acquire token lock for refresh; skipping this cycle")

    def _cleanup_previous(self, slot: TokenSlot) -> None:
        previous = slot.previous
        if previous is None:
            return
        if _utcnow() < previous.minted_at + self.cleanup_grace:
            return
        try:
            self.api_tokens_api.delete_api_token(
                previous.name,
                _request_timeout=MINT_REQUEST_TIMEOUT_SECONDS,
            )
        except NotFoundException:
            logger.debug("Previous API token '%s' already deleted", previous.name)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to delete previous API token '%s'", previous.name, exc_info=True)
            return
        slot.previous = None
        self._write_slot(slot)

    def _mint_and_persist(self, auth_token: str, previous_slot: Optional[TokenSlot]) -> None:
        self._set_api_token(auth_token)
        current_name = self._lookup_token_name(token_snippet(auth_token))
        new_name = _next_token_name(current_name)
        expires_at = _utcnow() + self.token_ttl
        created = self.api_tokens_api.create_api_token(
            ApiTokenRequest(name=new_name, expires_at=expires_at),
            _request_timeout=MINT_REQUEST_TIMEOUT_SECONDS,
        )
        minted_at = _utcnow()
        new_current = CachedToken(
            raw_key=created.raw_key,
            snippet=created.raw_key_snippet or token_snippet(created.raw_key),
            name=created.name,
            expires_at=created.expires_at or expires_at,
            minted_at=minted_at,
        )
        previous = None
        if previous_slot is not None:
            previous = PreviousToken(name=previous_slot.current.name, minted_at=previous_slot.current.minted_at)
        slot = TokenSlot(current=new_current, previous=previous)
        self._write_slot(slot)
        self._install_slot(slot)

    def _lookup_token_name(self, snippet: str) -> Optional[str]:
        """Find the name of the token matching ``snippet``.

        TODO: This temporarily pages through List API tokens and matches on
        raw_key_snippet. Before merging, switch callers to
        ``_get_token_name_by_snippet`` (GET /v1/api-tokens/by-snippet/{snippet})
        once that endpoint is live in production.
        """
        page = 1
        while True:
            response = self.api_tokens_api.list_api_tokens(
                page=page,
                page_size=100,
                _request_timeout=MINT_REQUEST_TIMEOUT_SECONDS,
            )
            results = response.results or []
            for token in results:
                if token.raw_key_snippet == snippet:
                    return token.name
            if not response.next:
                return None
            page += 1

    def _get_token_name_by_snippet(self, snippet: str) -> Optional[str]:
        """Look up a token name via GET /v1/api-tokens/by-snippet/{snippet}.

        TODO: Switch ``_lookup_token_name`` to call this before merging, once the
        by-snippet endpoint from zuuul PR #6579 is deployed. Do not call this yet;
        the endpoint is not live.
        """
        try:
            token = self.api_tokens_api.get_api_token_by_snippet(
                snippet,
                _request_timeout=MINT_REQUEST_TIMEOUT_SECONDS,
            )
        except NotFoundException:
            return None
        return token.name

    def _install_slot(self, slot: TokenSlot) -> None:
        self._slot = slot
        self._set_api_token(slot.current.raw_key)

    def _is_expired(self, token: CachedToken) -> bool:
        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return _utcnow() >= expires_at.astimezone(timezone.utc)

    def _read_slot(self) -> Optional[TokenSlot]:
        if not self._slot_path.exists():
            return None
        try:
            data = json.loads(self._slot_path.read_text(encoding="utf-8"))
            return TokenSlot.from_dict(data)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            logger.warning("Ignoring unreadable token cache file at %s", self._slot_path, exc_info=True)
            return None

    def _write_slot(self, slot: TokenSlot) -> None:
        payload = json.dumps(slot.to_dict(), indent=2, sort_keys=True)
        temp_path = self._slot_path.with_suffix(".tmp")
        try:
            fd = os.open(temp_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, self._slot_path)
            if os.name != "nt":
                os.chmod(self._slot_path, 0o600)
        except OSError as exc:
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except OSError:
                pass
            raise RuntimeError(f"Unable to write token cache file '{self._slot_path}'") from exc
