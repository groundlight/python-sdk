from unittest.mock import Mock

import pytest
from model import AccountMonthToDateInfo


def test_get_month_to_date_usage_success(gl):
    """Test successful retrieval of month-to-date usage information."""
    usage = gl.get_month_to_date_usage()

    # Verify the return type
    assert isinstance(usage, AccountMonthToDateInfo)

    # Verify all required fields are present and have correct types
    assert isinstance(usage.iqs, int)
    assert isinstance(usage.escalations, int)
    assert isinstance(usage.active_detectors, int)

    # Handle case where limits might be None (API may not provide limits)
    if usage.iqs_limit is not None:
        assert isinstance(usage.iqs_limit, int)
        assert usage.iqs_limit >= 0
    if usage.escalations_limit is not None:
        assert isinstance(usage.escalations_limit, int)
        assert usage.escalations_limit >= 0
    if usage.active_detectors_limit is not None:
        assert isinstance(usage.active_detectors_limit, int)
        assert usage.active_detectors_limit >= 0

    # Verify usage values are non-negative
    assert usage.iqs >= 0
    assert usage.escalations >= 0
    assert usage.active_detectors >= 0


def test_get_month_to_date_usage_with_mock():
    """Test get_month_to_date_usage with mocked API response."""
    from groundlight import Groundlight

    # Create mock response data
    mock_response_data = {
        "iqs": 150,
        "escalations": 25,
        "active_detectors": 10,
        "iqs_limit": 1000,
        "escalations_limit": 100,
        "active_detectors_limit": 50,
    }

    # Create mock API response object
    mock_api_response = Mock()
    mock_api_response.to_dict.return_value = mock_response_data

    # Create mock month_to_date_api
    mock_month_to_date_api = Mock()
    mock_month_to_date_api.month_to_date_account_info.return_value = mock_api_response

    # Create Groundlight instance and patch the month_to_date_api
    gl = Groundlight()
    gl.month_to_date_api = mock_month_to_date_api

    # Call the method
    usage = gl.get_month_to_date_usage()

    # Verify the API was called correctly
    mock_month_to_date_api.month_to_date_account_info.assert_called_once_with(
        _request_timeout=10  # DEFAULT_REQUEST_TIMEOUT
    )

    # Verify the response parsing
    assert isinstance(usage, AccountMonthToDateInfo)
    assert usage.iqs == 150
    assert usage.escalations == 25
    assert usage.active_detectors == 10
    assert usage.iqs_limit == 1000
    assert usage.escalations_limit == 100
    assert usage.active_detectors_limit == 50


def test_get_month_to_date_usage_api_error():
    """Test get_month_to_date_usage when API returns an error."""
    from groundlight import Groundlight
    from groundlight_openapi_client.exceptions import ApiException

    # Create mock month_to_date_api that raises an exception
    mock_month_to_date_api = Mock()
    mock_month_to_date_api.month_to_date_account_info.side_effect = ApiException(
        status=500, reason="Internal Server Error"
    )

    # Create Groundlight instance and patch the month_to_date_api
    gl = Groundlight()
    gl.month_to_date_api = mock_month_to_date_api

    # Verify the exception is raised
    with pytest.raises(ApiException) as exc_info:
        gl.get_month_to_date_usage()

    assert exc_info.value.status == 500
    assert "Internal Server Error" in str(exc_info.value)


def test_get_month_to_date_usage_unauthorized():
    """Test get_month_to_date_usage when unauthorized."""
    from groundlight import Groundlight
    from groundlight_openapi_client.exceptions import UnauthorizedException

    # Create mock month_to_date_api that raises an unauthorized exception
    mock_month_to_date_api = Mock()
    mock_month_to_date_api.month_to_date_account_info.side_effect = UnauthorizedException(
        status=401, reason="Unauthorized"
    )

    # Create Groundlight instance and patch the month_to_date_api
    gl = Groundlight()
    gl.month_to_date_api = mock_month_to_date_api

    # Verify the exception is raised
    with pytest.raises(UnauthorizedException) as exc_info:
        gl.get_month_to_date_usage()

    assert exc_info.value.status == 401
    assert "Unauthorized" in str(exc_info.value)


def test_get_month_to_date_usage_zero_values():
    """Test get_month_to_date_usage with zero values (new account scenario)."""
    from groundlight import Groundlight

    # Create mock response data with zero values
    mock_response_data = {
        "iqs": 0,
        "escalations": 0,
        "active_detectors": 0,
        "iqs_limit": 100,
        "escalations_limit": 10,
        "active_detectors_limit": 5,
    }

    # Create mock API response object
    mock_api_response = Mock()
    mock_api_response.to_dict.return_value = mock_response_data

    # Create mock month_to_date_api
    mock_month_to_date_api = Mock()
    mock_month_to_date_api.month_to_date_account_info.return_value = mock_api_response

    # Create Groundlight instance and patch the month_to_date_api
    gl = Groundlight()
    gl.month_to_date_api = mock_month_to_date_api

    # Call the method
    usage = gl.get_month_to_date_usage()

    # Verify the response parsing with zero values
    assert isinstance(usage, AccountMonthToDateInfo)
    assert usage.iqs == 0
    assert usage.escalations == 0
    assert usage.active_detectors == 0
    assert usage.iqs_limit == 100
    assert usage.escalations_limit == 10
    assert usage.active_detectors_limit == 5


def test_get_month_to_date_usage_usage_limits(gl):
    """Test that usage values don't exceed their limits."""
    usage = gl.get_month_to_date_usage()

    # Verify usage doesn't exceed limits (only if limits are provided)
    if usage.iqs_limit is not None:
        assert usage.iqs <= usage.iqs_limit
    if usage.escalations_limit is not None:
        assert usage.escalations <= usage.escalations_limit
    if usage.active_detectors_limit is not None:
        assert usage.active_detectors <= usage.active_detectors_limit


def test_get_month_to_date_usage_documentation_example(gl):
    """Test the example usage shown in the method's docstring."""
    usage = gl.get_month_to_date_usage()

    # Test the example from the docstring
    print(f"Image queries used: {usage.iqs} / {usage.iqs_limit}")
    print(f"Escalations used: {usage.escalations} / {usage.escalations_limit}")
    print(f"Active detectors: {usage.active_detectors} / {usage.active_detectors_limit}")

    # Verify the format is correct (this test mainly ensures the example runs without errors)
    assert isinstance(usage.iqs, int)
    # Handle case where limits might be None
    if usage.iqs_limit is not None:
        assert isinstance(usage.iqs_limit, int)
    if usage.escalations_limit is not None:
        assert isinstance(usage.escalations_limit, int)
    if usage.active_detectors_limit is not None:
        assert isinstance(usage.active_detectors_limit, int)
    assert isinstance(usage.escalations, int)
    assert isinstance(usage.active_detectors, int)


@pytest.mark.integration
def test_get_month_to_date_usage_integration(gl):
    """Integration test for get_month_to_date_usage with real API call."""
    usage = gl.get_month_to_date_usage()

    # Verify the response structure
    assert isinstance(usage, AccountMonthToDateInfo)

    # Verify all fields are present
    assert hasattr(usage, "iqs")
    assert hasattr(usage, "escalations")
    assert hasattr(usage, "active_detectors")
    assert hasattr(usage, "iqs_limit")
    assert hasattr(usage, "escalations_limit")
    assert hasattr(usage, "active_detectors_limit")

    # Verify data types
    assert isinstance(usage.iqs, int)
    assert isinstance(usage.escalations, int)
    assert isinstance(usage.active_detectors, int)

    # Handle case where limits might be None
    if usage.iqs_limit is not None:
        assert isinstance(usage.iqs_limit, int)
    if usage.escalations_limit is not None:
        assert isinstance(usage.escalations_limit, int)
    if usage.active_detectors_limit is not None:
        assert isinstance(usage.active_detectors_limit, int)

    # Verify logical constraints
    assert usage.iqs >= 0
    assert usage.escalations >= 0
    assert usage.active_detectors >= 0
    # Note: limits might be None, so we can't assert they're > 0
