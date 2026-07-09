from http import HTTPStatus
from io import BytesIO
from unittest.mock import Mock

from groundlight.client import Groundlight
from groundlight.experimental_api import ExperimentalApi
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


def test_api_client_replays_stream_body_after_unauthorized(mocker):
    """A 401 retry resends stream content instead of reusing a closed stream."""
    configuration = Configuration(host="https://example.com/device-api")
    client = GroundlightApiClient(configuration)
    client.set_unauthorized_handler(Mock())
    request_bodies = []

    def call_parent(*_args, **kwargs):
        """Consume each stream like the generated API client does."""
        request_bodies.append(kwargs["body"].read())
        kwargs["body"].close()
        if len(request_bodies) == 1:
            raise ApiException(status=401)
        return "success"

    mocker.patch.object(ApiClient, "call_api", side_effect=call_parent)
    body = BytesIO(b"image bytes")

    result = client.call_api("/v1/image-queries", "POST", {}, [], {}, body=body)

    assert result == "success"
    assert body.closed
    assert request_bodies == [b"image bytes", b"image bytes"]


def test_raw_request_recovers_and_retries_once_after_unauthorized(mocker):
    """Raw authenticated requests refresh their token and retry once after a 401."""
    configuration = Configuration(host="https://example.com/device-api")
    configuration.api_key["ApiToken"] = "old-token"
    client = GroundlightApiClient(configuration)

    def refresh_token() -> None:
        """Simulate replacing the rejected token."""
        configuration.api_key["ApiToken"] = "new-token"

    client.set_unauthorized_handler(refresh_token)
    unauthorized = Mock(status_code=HTTPStatus.UNAUTHORIZED)
    success = Mock(status_code=HTTPStatus.OK)
    request = mocker.patch("groundlight.internalapi.requests.request", side_effect=[unauthorized, success])

    response = client.request_with_unauthorized_recovery(
        "GET", "https://example.com/device-api/v1/detectors", headers={"x-api-token": "old-token"}
    )

    assert response is success
    assert request.call_count == EXPECTED_CALL_COUNT
    assert request.call_args_list[1].kwargs["headers"]["x-api-token"] == "new-token"


def test_create_note_uses_raw_request_token_recovery():
    """Note creation routes its multipart request through token recovery."""
    client = ExperimentalApi.__new__(ExperimentalApi)
    client.endpoint = "https://example.com/device-api"
    client.configuration = Configuration(host=client.endpoint)
    client.configuration.api_key["ApiToken"] = "old-token"
    client.api_client = Mock()
    client.api_client.request_with_unauthorized_recovery.return_value = Mock()

    client.create_note("detector-id", "note text", image=b"image bytes")

    request = client.api_client.request_with_unauthorized_recovery
    request.assert_called_once()
    assert request.call_args.args[:2] == ("POST", "https://example.com/device-api/v1/notes")
    assert request.call_args.kwargs["files"]["image"][1].read() == b"image bytes"
