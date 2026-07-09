from unittest.mock import Mock

from groundlight.client import Groundlight
from groundlight.internalapi import GroundlightApiClient
from groundlight_openapi_client import Configuration
from groundlight_openapi_client.api_client import ApiClient, ApiException

EXPECTED_CALL_COUNT = 2


def test_groundlight_starts_and_closes_token_manager(mocker):
    """Groundlight owns the token manager lifecycle and supports context management."""
    manager = Mock()
    token_manager_class = mocker.patch("groundlight.client.TokenManager", return_value=manager)
    mocker.patch.object(Groundlight, "_verify_connectivity")
    client = Groundlight(api_token="api_bootstrap_token_value_long_enough")
    api_client_close = mocker.patch.object(client.api_client, "close")

    with client as entered_client:
        assert entered_client is client
        token_manager_class.assert_called_once()
        manager.start.assert_called_once()

    manager.close.assert_called_once()
    api_client_close.assert_called_once()


def test_api_client_recovers_and_retries_once_after_unauthorized(mocker):
    """The custom API client refreshes credentials and retries one failed request."""
    configuration = Configuration(host="https://example.com/device-api")
    client = GroundlightApiClient(configuration)
    handler = Mock()
    client.set_unauthorized_handler(handler)
    parent_call = mocker.patch.object(ApiClient, "call_api", side_effect=[ApiException(status=401), "success"])

    result = client.call_api("/v1/test", "GET", {}, [], {})

    assert result == "success"
    handler.assert_called_once_with()
    assert parent_call.call_count == EXPECTED_CALL_COUNT
