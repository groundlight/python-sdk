from unittest.mock import Mock

from groundlight.client import Groundlight


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


def test_groundlight_skips_token_manager_when_rotation_disabled(mocker):
    """Disabling rotation leaves the configured token in place with no TokenManager."""
    token_manager_class = mocker.patch("groundlight.client.TokenManager")
    mocker.patch.object(Groundlight, "_verify_connectivity")

    client = Groundlight(api_token="api_bootstrap_token_value_long_enough", enable_token_rotation=False)
    api_client_close = mocker.patch.object(client.api_client, "close")
    client.close()

    token_manager_class.assert_not_called()
    assert client._token_manager is None
    assert client.configuration.api_key["ApiToken"] == "api_bootstrap_token_value_long_enough"
    api_client_close.assert_called_once()
