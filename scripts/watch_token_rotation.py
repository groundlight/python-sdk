#!/usr/bin/env python3
"""Poll whoami against api.dev and print the live token cache for rotation testing.

Requires GROUNDLIGHT_API_TOKEN for a token that can mint on the target environment.

Example:
    poetry run python scripts/watch_token_rotation.py
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from groundlight import Groundlight
from groundlight.config import DISABLE_TOKEN_REFRESH_VARIABLE_NAME

DEV_ENDPOINT = "https://api.dev.groundlight.ai/"
POLL_SECONDS = 1


def _active_token(gl: Groundlight) -> str:
    """Return the API token currently configured on the client."""
    return gl.configuration.api_key["ApiToken"]


def _slot_path(gl: Groundlight) -> Path:
    """Return the on-disk token cache path for this client's bootstrap snippet."""
    return gl._token_manager._slot_path  # pylint: disable=protected-access


def main() -> None:
    """Create a client and print whoami + token cache every few seconds."""
    # Ensure background refresh is on even if a prior test session exported the disable flag.
    os.environ.pop(DISABLE_TOKEN_REFRESH_VARIABLE_NAME, None)

    if not os.environ.get("GROUNDLIGHT_API_TOKEN"):
        raise SystemExit("Set GROUNDLIGHT_API_TOKEN before running this script.")

    with Groundlight(endpoint=DEV_ENDPOINT) as gl:
        slot_path = _slot_path(gl)
        print(f"endpoint={gl.endpoint}")
        print(f"slot_path={slot_path}")
        print(f"polling whoami every {POLL_SECONDS}s (Ctrl-C to stop)\n")

        while True:
            user = gl.whoami()
            token = _active_token(gl)
            print("=" * 60)
            print(time.time())
            print(f"whoami: {user}")
            print(f"active token snippet: {token[:20]}")
            print(f"cache file: {slot_path}")
            if slot_path.exists():
                print(json.dumps(json.loads(slot_path.read_text(encoding="utf-8")), indent=2))
            else:
                print("(cache file missing)")
            print()
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
