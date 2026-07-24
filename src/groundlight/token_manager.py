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
from groundlight_openapi_client.exceptions import ApiException, NotFoundException, UnauthorizedException
from groundlight_openapi_client.model.api_token import ApiToken
from groundlight_openapi_client.model.api_token_create_response import ApiTokenCreateResponse
from groundlight_openapi_client.model.api_token_request import ApiTokenRequest
from platformdirs import user_data_path

from groundlight.internalapi import GroundlightApiClient, api_exception_detail

logger = logging.getLogger("groundlight.sdk")

TOKEN_SNIPPET_LENGTH = 20
# Refresh fires after this fraction of the server-reported token lifetime
# (expires_at - created_at). Example: 30-day TTL => refresh every 1 day.
REFRESH_INTERVAL_FRACTION = 1 / 30
TOKEN_NAME_MAX_LENGTH = 64
TOKEN_NAME_SUFFIX_LENGTH = 7
LOCK_TIMEOUT_SECONDS = 60
# After a failed background refresh the current token is still valid for the rest of its
# TTL, so retry on a short cadence to recover quickly from a transient outage rather than
# waiting a full refresh interval (which would also spin when the token is already overdue).
# Also used as the floor when server lifetime is non-positive (clock skew).
REFRESH_RETRY_BACKOFF_SECONDS = 5 * 60
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
    """Store the working token data needed for authentication and rotation.

    expires_at comes from the server. minted_at is the local observation time used to
    schedule refresh. ttl is the server-side lifetime (expires_at - created_at) used to
    compute the refresh cadence without mixing server and client clocks.
    """

    raw_key: str
    snippet: str
    name: str
    expires_at: Optional[datetime]
    minted_at: datetime
    ttl: Optional[timedelta]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CurrentToken":
        """Build a current token from its on-disk representation."""
        expires_raw = data.get("expires_at")
        ttl_seconds = data["ttl_seconds"]
        return cls(
            raw_key=data["raw_key"],
            snippet=data["snippet"],
            name=data["name"],
            expires_at=_parse_datetime(expires_raw) if expires_raw is not None else None,
            minted_at=_parse_datetime(data["minted_at"]),
            ttl=timedelta(seconds=ttl_seconds) if ttl_seconds is not None else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the current token to its JSON-compatible representation."""
        return {
            "raw_key": self.raw_key,
            "snippet": self.snippet,
            "name": self.name,
            "expires_at": _format_datetime(self.expires_at) if self.expires_at is not None else None,
            "minted_at": _format_datetime(self.minted_at),
            "ttl_seconds": self.ttl.total_seconds() if self.ttl is not None else None,
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

    base_name is the configured token's human-readable name with any auto-generated suffix
    stripped. It is established once at first mint and reused for all future rotations.
    """

    base_name: str
    current: CurrentToken
    previous: Optional[PreviousToken] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenSlot":
        """Build a token slot from its on-disk representation."""
        previous_data = data.get("previous")
        return cls(
            base_name=data["base_name"],
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
        configured_token: str,
        configuration: Configuration,
        request_timeout: float,
        token_dir: Optional[Path] = None,
    ):
        """Initialize the cache slot and select or mint a working API token."""
        self._configured_token = configured_token
        self._configured_snippet = configured_token[:TOKEN_SNIPPET_LENGTH]
        if len(self._configured_snippet) != TOKEN_SNIPPET_LENGTH or not re.fullmatch(
            r"[A-Za-z0-9_]+", self._configured_snippet
        ):
            raise TokenManagerError(
                "The configured API token has an invalid format. Check that GROUNDLIGHT_API_TOKEN is set correctly."
            )
        self._configuration = configuration
        self._request_timeout = request_timeout
        self._token_dir = token_dir or self._default_token_dir()
        self._slot_path = self._token_dir / f"{self._configured_snippet}.json"
        self._lock_path = self._token_dir / f"{self._configured_snippet}.lock"
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
        """Load a valid cached token, use a never-expire configured token, or mint a child."""
        try:
            with self._lock:
                slot = self._load_slot()
                if slot and self._is_usable_cached_token(slot.current):
                    self._activate(slot.current)
                    return

                self._set_api_token(self._configured_token)
                try:
                    configured_meta = self._get_token_by_snippet(self._configured_snippet)
                except NotFoundException:
                    # Token management API unavailable: keep the configured token as-is.
                    logger.warning(
                        "Automatic API token refresh is unavailable because this server does not support token"
                        " management"
                    )
                    self._available = False
                    return

                if configured_meta.expires_at is None:
                    # Never-expire configured token: behave like pre-rotation Groundlight.
                    return

                base_name = TOKEN_NAME_SUFFIX_PATTERN.sub("", configured_meta.name)
                self._mint_replacement(
                    base_name=base_name,
                    previous=PreviousToken(name=configured_meta.name, minted_at=_utc_now()),
                )
        except FileLockTimeout as exc:
            raise TokenManagerError(f"Timed out waiting for token cache lock '{self._lock_path}'") from exc
        except NotFoundException:
            logger.warning(
                "Automatic API token refresh is unavailable because this server does not support token management"
            )
            self._available = False
            self._set_api_token(self._configured_token)
        except UnauthorizedException as exc:
            detail = api_exception_detail(exc) or "API token was rejected"
            raise TokenManagerError(detail) from exc
        except TokenManagerError:
            raise
        except Exception as exc:  # pylint: disable=broad-exception-caught
            raise TokenManagerError(
                "Unable to create a working API token. "
                "Check that GROUNDLIGHT_API_TOKEN is set to a valid token for this endpoint."
            ) from exc

    @staticmethod
    def _is_usable_cached_token(token: CurrentToken) -> bool:
        """Whether a cached token can be activated without minting."""
        if token.expires_at is None:
            return True
        return token.expires_at > _utc_now()

    def start(self) -> None:
        """Start background refresh when the working token has a finite lifetime."""
        if not self._available or self._thread is not None:
            return
        if self._current is None or self._current.ttl is None:
            return
        self._thread = threading.Thread(
            target=self._run,
            name=f"gl-token-refresh-{self._configured_snippet[:8]}",
            daemon=True,
        )
        self._thread.start()

    def close(self) -> None:
        """Stop background refresh work and close its API client."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
        self._rotation_client.close()

    def refresh(self) -> bool:
        """Use the cached token if it is still fresh; otherwise rotate under the file lock.

        Rotation always completes the two-token cycle: revoke previous (best effort), demote
        current to previous, and mint a new current. Returns False only when rotation could
        not run (lock timeout, mint failure, or token API unavailable).
        """
        try:
            with self._lock:
                slot = self._load_slot()
                if slot is None:
                    raise TokenManagerError(
                        "Token cache slot is missing and cannot be refreshed. "
                        "Please provision a new GROUNDLIGHT_API_TOKEN."
                    )

                self._activate(slot.current)
                if slot.current.expires_at is None or slot.current.ttl is None:
                    return True
                if _utc_now() - slot.current.minted_at < self._refresh_interval(slot.current):
                    return True
                self._revoke_previous(slot.previous)
                self._mint_replacement(
                    base_name=slot.base_name,
                    previous=PreviousToken(name=slot.current.name, minted_at=slot.current.minted_at),
                )
                return True
        except TokenManagerError:
            raise
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
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning("Automatic API token refresh failed; the current token remains active", exc_info=True)
            return False

    def _run(self) -> None:
        """Refresh tokens on schedule until the client is closed."""
        while not self._stop_event.is_set():
            current = self._current
            if current is None or current.expires_at is None or current.ttl is None:
                return
            refresh_at = current.minted_at + self._refresh_interval(current)
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

    @staticmethod
    def _refresh_interval(token: CurrentToken) -> timedelta:
        """Return how long to keep a working token before rotating.

        Uses the server-reported lifetime so client clock skew cannot invent a negative
        interval. Non-positive lifetimes fall back to the retry backoff to avoid a spin.
        """
        if token.ttl is None:
            raise TokenManagerError("Cannot compute a refresh interval for a never-expiring token")
        interval = token.ttl * REFRESH_INTERVAL_FRACTION
        if interval <= timedelta(0):
            return timedelta(seconds=REFRESH_RETRY_BACKOFF_SECONDS)
        return interval

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

    def _mint_replacement(self, base_name: str, previous: Optional[PreviousToken]) -> CurrentToken:
        """Mint a new token, persist the updated slot, and activate the new credential."""
        new_name = self._new_token_name(base_name)
        minted_at = _utc_now()
        # Omit expires_at so the server applies the identity's token lifetime policy.
        response = self._api_tokens.create_api_token(
            ApiTokenRequest(name=new_name),
            _request_timeout=self._request_timeout,
        )
        current = self._current_from_response(response, minted_at)
        self._write_slot(TokenSlot(base_name=base_name, current=current, previous=previous))
        self._activate(current)
        return current

    def _get_token_by_snippet(self, snippet: str) -> ApiToken:
        """Retrieve token metadata by snippet via the dedicated API endpoint."""
        return self._api_tokens.get_api_token_by_snippet(snippet, _request_timeout=self._request_timeout)

    def _revoke_previous(self, previous: Optional[PreviousToken]) -> None:
        """Best-effort revoke of the demoted previous token before it is replaced in the slot."""
        if previous is None:
            return
        try:
            self._api_tokens.delete_api_token(previous.name, _request_timeout=self._request_timeout)
        except NotFoundException:
            logger.debug("Previous API token '%s' was already deleted", previous.name)
        except ApiException:
            logger.warning(
                "Unable to delete previous API token '%s'; continuing rotation",
                previous.name,
                exc_info=True,
            )

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
            return CurrentToken(
                raw_key=response.raw_key,
                snippet=response.raw_key_snippet,
                name=response.name,
                expires_at=None,
                minted_at=minted_at,
                ttl=None,
            )
        expires_at = _normalize_datetime(response.expires_at)
        created_at = _normalize_datetime(response.created_at)
        return CurrentToken(
            raw_key=response.raw_key,
            snippet=response.raw_key_snippet,
            name=response.name,
            expires_at=expires_at,
            minted_at=minted_at,
            ttl=expires_at - created_at,
        )

    def _activate(self, token: CurrentToken) -> None:
        """Use a cached token for subsequent SDK API calls."""
        self._current = token
        self._set_api_token(token.raw_key)

    def _set_api_token(self, token: str) -> None:
        """Update the shared OpenAPI configuration with an API token."""
        self._configuration.api_key["ApiToken"] = token
