from unittest.mock import Mock

from groundlight.client import Groundlight
from groundlight.experimental_api import ExperimentalApi


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
        assert token_manager_class.call_args.kwargs["enable_token_rotation"] is True
        manager.start.assert_called_once()

    manager.close.assert_called_once()
    api_client_close.assert_called_once()


def test_groundlight_forwards_enable_token_rotation(mocker):
    """Groundlight passes enable_token_rotation through to TokenManager."""
    manager = Mock()
    token_manager_class = mocker.patch("groundlight.client.TokenManager", return_value=manager)
    mocker.patch.object(Groundlight, "_verify_connectivity")

    client = Groundlight(api_token="api_bootstrap_token_value_long_enough", enable_token_rotation=False)
    client.close()

    assert token_manager_class.call_args.kwargs["enable_token_rotation"] is False


def test_experimental_api_forwards_enable_token_rotation(mocker):
    """ExperimentalApi passes enable_token_rotation through to TokenManager."""
    manager = Mock()
    token_manager_class = mocker.patch("groundlight.client.TokenManager", return_value=manager)
    mocker.patch.object(Groundlight, "_verify_connectivity")

    client = ExperimentalApi(api_token="api_bootstrap_token_value_long_enough", enable_token_rotation=False)
    client.close()

    assert token_manager_class.call_args.kwargs["enable_token_rotation"] is False
