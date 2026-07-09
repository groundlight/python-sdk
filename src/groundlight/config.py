API_TOKEN_WEB_URL = "https://dashboard.groundlight.ai/reef/my-account/api-tokens"
API_TOKEN_VARIABLE_NAME = "GROUNDLIGHT_API_TOKEN"

DEFAULT_ENDPOINT = "https://api.groundlight.ai/"
DISABLE_TLS_VARIABLE_NAME = "DISABLE_TLS_VERIFY"

# Auto-refresh of API tokens. The SDK mints short-lived tokens and rotates them
# on a background thread so that a long-lived bootstrap token is never used
# directly for API calls. See token_manager.py.
TOKEN_DIR_VARIABLE_NAME = "GROUNDLIGHT_TOKEN_DIR"
DEFAULT_TOKEN_DIR = "~/.groundlight/tokens"
# Rollout gate. The plan's end state is auto-refresh always-on, but the required
# server endpoints (mint/list/delete, and get-by-snippet) are not yet live in all
# environments. Until they are, auto-refresh is opt-in via this env var (or the
# auto_refresh_token= constructor argument) so upgrading the SDK cannot break
# clients pointed at an endpoint that lacks the token-management API.
# TODO(GL-1709): flip the default to on once the server endpoints are deployed.
AUTO_REFRESH_TOKEN_VARIABLE_NAME = "GROUNDLIGHT_AUTO_REFRESH_TOKEN"
TOKEN_TTL_DAYS = 30  # expires_at = now + TOKEN_TTL_DAYS when minting
REFRESH_INTERVAL_DAYS = 1  # mint a fresh token at most once per day
CLEANUP_GRACE_FACTOR = 2  # delete the previous token CLEANUP_GRACE_FACTOR * REFRESH_INTERVAL_DAYS after replacing it


__all__ = [
    "API_TOKEN_WEB_URL",
    "API_TOKEN_VARIABLE_NAME",
    "DEFAULT_ENDPOINT",
    "DISABLE_TLS_VARIABLE_NAME",
    "TOKEN_DIR_VARIABLE_NAME",
    "DEFAULT_TOKEN_DIR",
    "AUTO_REFRESH_TOKEN_VARIABLE_NAME",
    "TOKEN_TTL_DAYS",
    "REFRESH_INTERVAL_DAYS",
    "CLEANUP_GRACE_FACTOR",
]

API_TOKEN_MISSING_HELP_MESSAGE = (
    "No API token found. Please put your token in an environment variable "
    f'named "{API_TOKEN_VARIABLE_NAME}". If you don\'t have a token, you can '
    f"create one at {API_TOKEN_WEB_URL}"
)
