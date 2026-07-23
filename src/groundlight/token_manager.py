import json
import logging
import os
import re
import secrets
import tempfile
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from filelock import FileLock
from filelock import Timeout as FileLockTimeout
from groundlight_openapi_client import Configuration
from groundlight_openapi_client.api.api_tokens_api import ApiTokensApi
from groundlight_openapi_client.exceptions import ApiException, NotFoundException
from groundlight_openapi_client.model.api_token import ApiToken
from groundlight_openapi_client.model.api_token_create_response import ApiTokenCreateResponse
from groundlight_openapi_client.model.api_token_request import ApiTokenRequest
from platformdirs import user_data_path

from groundlight.internalapi import GroundlightApiClient

logger = logging.getLogger("groundlight.sdk")

TOKEN_SNIPPET_LENGTH = 20
# TODO(GL-1709): TEMPORARY short-lived values for live rotation testing only.
# Before merge / production: set TOKEN_TTL_DAYS = 30 and REFRESH_INTERVAL_DAYS = 1.
# Follow-up (after zuuul exposes identity token_ttl on public /v1/api-tokens):
# - discover rotate-vs-not from by-snippet token_ttl (null => no refresh thread)
# - derive refresh_interval from mint expires_at as observed_ttl / 30
# - stop hardcoding TOKEN_TTL_DAYS / REFRESH_INTERVAL_DAYS
TOKEN_TTL_DAYS = 3 / (24 * 60)  # TODO(GL-1709): testing only (3 minutes); revert to 30
REFRESH_INTERVAL_DAYS = 1 / (24 * 60)  # TODO(GL-1709): testing only (1 minute); revert to 1
CLEANUP_GRACE_FACTOR = 2
TOKEN_NAME_MAX_LENGTH = 64
TOKEN_NAME_SUFFIX_LENGTH = 7
LOCK_TIMEOUT_SECONDS = 60
# After a failed background refresh the current token is still valid for the rest of its
# TTL, so retry on a short cadence to recover quickly from a transient outage rather than
# waiting a full refresh interval (which would also spin when the token is already overdue).
REFRESH_RETRY_BACKOFF_SECONDS = 5 * 60
# Matches the trailing " xxxxxx" hex suffix this class appends, so repeated rotations
# reuse a stable base name instead of accreting a new suffix each cycle.
TOKEN_NAME_SUFFIX_PATTERN = re.compile(r" [0-9a-f]{6}$")


class TokenManagerError(RuntimeError):
    """Raised when the SDK cannot initialize or refresh its working API token."""


def _utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def _parse_datetime(value: str) -> datetime:
    """Parse an ISO 8601 timestamp and normalize it to UTC."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_datetime(value: datetime) -> str:
    """Format a datetime as an ISO 8601 UTC timestamp."""
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_datetime(value: datetime) -> datetime:
    """Normalize a datetime to a timezone-aware UTC value."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class CurrentToken:
    """Store the working token data needed for authentication and rotation."""

    raw_key: str
    snippet: str
    name: str
    expires_at: datetime
    minted_at: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CurrentToken":
        """Build a current token from its on-disk representation."""
        return cls(
            raw_key=data["raw_key"],
            snippet=data["snippet"],
            name=data["name"],
            expires_at=_parse_datetime(data["expires_at"]),
            minted_at=_parse_datetime(data["minted_at"]),
        )

    def to_dict(self) -> Dict[str, str]:
        """Convert the current token to its JSON-compatible representation."""
        return {
            "raw_key": self.raw_key,
            "snippet": self.snippet,
            "name": self.name,
            "expires_at": _format_datetime(self.expires_at),
            "minted_at": _format_datetime(self.minted_at),
        }


@dataclass(frozen=True)
class PreviousToken:
    """Store the superseded token metadata needed for delayed cleanup."""

    name: str
    minted_at: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PreviousToken":
        """Build previous-token metadata from its on-disk representation."""
        return cls(name=data["name"], minted_at=_parse_datetime(data["minted_at"]))

    def to_dict(self) -> Dict[str, str]:
        """Convert previous-token metadata to its JSON-compatible representation."""
        return {"name": self.name, "minted_at": _format_datetime(self.minted_at)}


@dataclass(frozen=True)
class TokenSlot:
    """Represent the current and previous tokens stored in one cache slot.

    base_name is the bootstrap token's human-readable name with any auto-generated suffix
    stripped. It is established once at first mint and reused for all future rotations,
    so a token chain always looks like "My Sensor ab12cd", "My Sensor ef34gh", ... rather
    than accumulating nested suffixes.
    """

    base_name: str
    current: CurrentToken
    previous: Optional[PreviousToken] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenSlot":
        """Build a token slot from its on-disk representation."""
        previous_data = data.get("previous")
        return cls(
            # Empty string for slots written before this field existed; callers fall back
            # to a live lookup when base_name is empty.
            base_name=data.get("base_name", ""),
            current=CurrentToken.from_dict(data["current"]),
            previous=PreviousToken.from_dict(previous_data) if previous_data else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the token slot to its JSON-compatible representation."""
        return {
            "base_name": self.base_name,
            "current": self.current.to_dict(),
            "previous": self.previous.to_dict() if self.previous else None,
        }


class TokenManager:  # pylint: disable=too-many-instance-attributes
    """Manage cached API tokens and coordinate their automatic rotation."""

    def __init__(
        self,
        bootstrap_token: str,
        configuration: Configuration,
        request_timeout: float,
        token_dir: Optional[Path] = None,
    ):
        """Initialize the cache slot and select or mint a working API token."""
        self._bootstrap_token = bootstrap_token
        self._bootstrap_snippet = bootstrap_token[:TOKEN_SNIPPET_LENGTH]
        if len(self._bootstrap_snippet) != TOKEN_SNIPPET_LENGTH or not re.fullmatch(
            r"[A-Za-z0-9_]+", self._bootstrap_snippet
        ):
            raise TokenManagerError("The bootstrap API token has an invalid format")
        self._configuration = configuration
        self._request_timeout = request_timeout
        self._token_dir = token_dir or self._default_token_dir()
        self._slot_path = self._token_dir / f"{self._bootstrap_snippet}.json"
        self._lock_path = self._token_dir / f"{self._bootstrap_snippet}.lock"
        self._lock = FileLock(str(self._lock_path), timeout=LOCK_TIMEOUT_SECONDS, mode=0o600)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._current: Optional[CurrentToken] = None
        self._available = True

        self._ensure_token_dir()
        self._rotation_client = GroundlightApiClient(configuration)
        self._api_tokens = ApiTokensApi(self._rotation_client)
        self._initialize_token()

    @staticmethod
    def _default_token_dir() -> Path:
        """Return the platform-appropriate token cache directory."""
        configured_dir = os.environ.get("GROUNDLIGHT_TOKEN_DIR")
        if configured_dir:
            return Path(configured_dir).expanduser()
        if os.name == "nt":
            return user_data_path("Groundlight") / "tokens"
        return Path.home() / ".groundlight" / "tokens"

    def _ensure_token_dir(self) -> None:
        """Create the token directory, tighten its permissions, or raise a clear error."""
        try:
            self._token_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
            # mkdir does not alter an existing directory's mode, so tighten it explicitly:
            # cached tokens are secrets and must not be group- or world-readable.
            if os.name != "nt":
                os.chmod(self._token_dir, 0o700)
        except OSError as exc:
            raise TokenManagerError(f"Cannot create Groundlight token directory '{self._token_dir}': {exc}") from exc
        if not os.access(self._token_dir, os.W_OK):
            raise TokenManagerError(f"Groundlight token directory '{self._token_dir}' is not writable")

    def _initialize_token(self) -> None:
        """Load a valid cached token or mint one from the configured bootstrap token."""
        try:
            with self._lock:
                slot = self._load_slot()
                if slot and slot.current.expires_at > _utc_now():
                    self._activate(slot.current)
                    return
                self._set_api_token(self._bootstrap_token)
                # Look up the bootstrap token once: its name seeds base_name for every future
                # rotation, and we park that name as previous for delayed cleanup (not immediate revoke).
                try:
                    bootstrap_meta = self._get_token_by_snippet(self._bootstrap_snippet)
                    base_name = TOKEN_NAME_SUFFIX_PATTERN.sub("", bootstrap_meta.name)
                    bootstrap_previous: Optional[PreviousToken] = PreviousToken(
                        name=bootstrap_meta.name, minted_at=_utc_now()
                    )
                except NotFoundException:
                    base_name = "sdk-auto"
                    bootstrap_previous = None
                self._mint_replacement(
                    base_name=base_name,
                    slot=slot,
                    record_replaced_current=False,
                    previous=bootstrap_previous,
                )
        except FileLockTimeout as exc:
            raise TokenManagerError(f"Timed out waiting for token cache lock '{self._lock_path}'") from exc
        except NotFoundException:
            logger.warning(
                "Automatic API token refresh is unavailable because this server does not support token management"
            )
            self._available = False
            self._set_api_token(self._bootstrap_token)
        except TokenManagerError:
            raise
        except Exception as exc:
            raise TokenManagerError("Unable to mint a working API token with the bootstrap token") from exc

    def start(self) -> None:
        """Start background refresh when the server supports token management."""
        if not self._available or self._thread is not None:
            return
        self._thread = threading.Thread(
            target=self._run,
            name=f"gl-token-refresh-{self._bootstrap_snippet[:8]}",
            daemon=True,
        )
        self._thread.start()

    def close(self) -> None:
        """Stop background refresh work and close its API client."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
        self._rotation_client.close()

    def recover_from_unauthorized(self) -> None:
        """Recover from a 401 by loading a fresher cached token written by another process.

        Does not remint from the configured bootstrap token. If no fresher token is available
        on disk, the working token chain is broken and requires human intervention
        (provision a new GROUNDLIGHT_API_TOKEN).
        """
        if not self._available:
            raise TokenManagerError("Automatic token recovery is unavailable on this server")
        failed_token = self._configuration.api_key["ApiToken"]
        try:
            with self._lock:
                slot = self._load_slot()
                if slot and slot.current.raw_key != failed_token and slot.current.expires_at > _utc_now():
                    self._activate(slot.current)
                    return
                raise TokenManagerError(
                    "The working API token was rejected and no fresher cached token is available. "
                    "Please provision a new GROUNDLIGHT_API_TOKEN."
                )
        except FileLockTimeout as exc:
            raise TokenManagerError("Timed out waiting to recover from an unauthorized API response") from exc
        except TokenManagerError:
            raise
        except Exception as exc:
            raise TokenManagerError("The cached token was rejected and could not be replaced") from exc

    def refresh(self) -> bool:
        """Refresh the working token, returning whether the cycle completed successfully."""
        try:
            with self._lock:
                slot = self._load_slot()
                if slot is None:
                    raise TokenManagerError(
                        "Token cache slot is missing and cannot be refreshed. "
                        "Please provision a new GROUNDLIGHT_API_TOKEN."
                    )

                self._activate(slot.current)
                if _utc_now() - slot.current.minted_at < timedelta(days=REFRESH_INTERVAL_DAYS):
                    return True
                if not self._cleanup_previous(slot.previous):
                    return False
                # Read base_name from slot; fall back to a live lookup for old-format slots.
                base_name = slot.base_name or self._resolve_base_name(slot.current.snippet)
                self._mint_replacement(base_name=base_name, slot=slot)
                return True
        except NotFoundException:
            logger.warning(
                "Automatic API token refresh is unavailable because this server does not support token management"
            )
            self._available = False
            self._stop_event.set()
            return False
        except FileLockTimeout:
            logger.warning("Skipping token refresh because the cache lock could not be acquired")
            return False

    def _run(self) -> None:
        """Refresh tokens on schedule until the client is closed."""
        while not self._stop_event.is_set():
            current = self._current
            if current is None:
                wait_seconds = 0.0
            else:
                refresh_at = current.minted_at + timedelta(days=REFRESH_INTERVAL_DAYS)
                wait_seconds = max(0.0, (refresh_at - _utc_now()).total_seconds())
            if self._stop_event.wait(wait_seconds):
                return
            try:
                refresh_succeeded = self.refresh()
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("Automatic API token refresh failed; the current token remains active", exc_info=True)
                refresh_succeeded = False
            if not refresh_succeeded and self._stop_event.wait(REFRESH_RETRY_BACKOFF_SECONDS):
                return

    def _load_slot(self) -> Optional[TokenSlot]:
        """Load the cache slot, returning None when it does not exist."""
        if not self._slot_path.exists():
            return None
        try:
            with self._slot_path.open(encoding="utf-8") as slot_file:
                return TokenSlot.from_dict(json.load(slot_file))
        except (KeyError, TypeError, ValueError, OSError) as exc:
            raise TokenManagerError(f"Cannot read Groundlight token cache '{self._slot_path}': {exc}") from exc

    def _write_slot(self, slot: TokenSlot) -> None:
        """Atomically write a private token cache slot."""
        temporary_path: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._token_dir,
                prefix=f".{self._slot_path.name}.",
                delete=False,
            ) as temporary_file:
                temporary_path = temporary_file.name
                json.dump(slot.to_dict(), temporary_file, indent=2)
                temporary_file.write("\n")
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.chmod(temporary_path, 0o600)
            os.replace(temporary_path, self._slot_path)
        except OSError as exc:
            raise TokenManagerError(f"Cannot write Groundlight token cache '{self._slot_path}': {exc}") from exc
        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.unlink(temporary_path)

    def _mint_replacement(
        self,
        base_name: str,
        slot: Optional[TokenSlot],
        *,
        record_replaced_current: bool = True,
        previous: Optional[PreviousToken] = None,
    ) -> CurrentToken:
        """Mint a new token, persist the updated slot, and activate the new credential."""
        new_name = self._new_token_name(base_name)
        minted_at = _utc_now()
        response = self._api_tokens.create_api_token(
            ApiTokenRequest(name=new_name, expires_at=minted_at + timedelta(days=TOKEN_TTL_DAYS)),
            _request_timeout=self._request_timeout,
        )
        current = self._current_from_response(response, minted_at)
        if previous is not None:
            next_previous = previous
        elif slot and record_replaced_current:
            next_previous = PreviousToken(name=slot.current.name, minted_at=slot.current.minted_at)
        else:
            next_previous = slot.previous if slot else None
        self._write_slot(TokenSlot(base_name=base_name, current=current, previous=next_previous))
        self._activate(current)
        return current

    def _resolve_base_name(self, snippet: str) -> str:
        """Look up a token by snippet and return its name with any auto-generated suffix stripped.

        Used when reading an old-format slot file that predates the base_name field.
        Falls back to 'sdk-auto' when no matching token is found.
        """
        try:
            token = self._get_token_by_snippet(snippet)
            return TOKEN_NAME_SUFFIX_PATTERN.sub("", token.name)
        except NotFoundException:
            return "sdk-auto"

    def _get_token_by_snippet(self, snippet: str) -> ApiToken:
        """Retrieve token metadata by snippet via the dedicated API endpoint."""
        return self._api_tokens.get_api_token_by_snippet(snippet, _request_timeout=self._request_timeout)

    def _cleanup_previous(self, previous: Optional[PreviousToken]) -> bool:
        """Delete due token metadata, returning whether it is safe to replace the slot."""
        if previous is None:
            return True
        grace_period = timedelta(days=CLEANUP_GRACE_FACTOR * REFRESH_INTERVAL_DAYS)
        if _utc_now() - previous.minted_at < grace_period:
            return False
        try:
            self._api_tokens.delete_api_token(previous.name, _request_timeout=self._request_timeout)
        except NotFoundException:
            logger.debug("Previous API token '%s' was already deleted", previous.name)
        except ApiException:
            logger.warning("Unable to delete previous API token '%s'", previous.name, exc_info=True)
            return False
        return True

    @staticmethod
    def _new_token_name(base_name: str) -> str:
        """Append a unique 6-character hex suffix to base_name, truncating to fit the column limit."""
        suffix = secrets.token_hex(3)
        max_base_length = TOKEN_NAME_MAX_LENGTH - TOKEN_NAME_SUFFIX_LENGTH
        return f"{base_name[:max_base_length]} {suffix}"

    @staticmethod
    def _current_from_response(response: ApiTokenCreateResponse, minted_at: datetime) -> CurrentToken:
        """Convert a token creation response into cached current-token data."""
        if response.expires_at is None:
            # TODO(GL-1709): null expires_at means a never-expire identity. Once token_ttl
            # discovery lands, skip the refresh loop instead of inventing a client-side expiry.
            expires_at = minted_at + timedelta(days=TOKEN_TTL_DAYS)
        else:
            expires_at = _normalize_datetime(response.expires_at)
        return CurrentToken(
            raw_key=response.raw_key,
            snippet=response.raw_key_snippet,
            name=response.name,
            expires_at=expires_at,
            minted_at=minted_at,
        )

    def _activate(self, token: CurrentToken) -> None:
        """Use a cached token for subsequent SDK API calls."""
        self._current = token
        self._set_api_token(token.raw_key)

    def _set_api_token(self, token: str) -> None:
        """Update the shared OpenAPI configuration with an API token."""
        self._configuration.api_key["ApiToken"] = token
