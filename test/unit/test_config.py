import pytest

from groundlight.internalapi import sanitize_endpoint_url


def test_invalid_endpoint_config():
    BAD_ENDPOINTS = [
        "Just a string",
        "foo://bar",
        "http://bar/?foo=123",
        "http://bar/asdlkfj#123",
        "hxxp://bar/asdlkfj",
        "https://api.groundlight.ai/device-api/?bad",
        "https://api.groundlight.ai/?bad",
        "https://api.groundlight.ai/#bad",
    ]
    for endpoint in BAD_ENDPOINTS:
        with pytest.raises(ValueError):
            out = sanitize_endpoint_url(endpoint)


def test_endpoint_cleanup():
    expected = "https://api.groundlight.ai/device-api"
    assert sanitize_endpoint_url("https://api.groundlight.ai") == expected
    assert sanitize_endpoint_url("https://api.groundlight.ai/") == expected
    assert sanitize_endpoint_url("https://api.groundlight.ai/device-api") == expected
    assert sanitize_endpoint_url("https://api.groundlight.ai/device-api/") == expected

    expected = "https://api.integ.groundlight.ai/device-api"
    assert sanitize_endpoint_url("https://api.integ.groundlight.ai") == expected
    assert sanitize_endpoint_url("https://api.integ.groundlight.ai/") == expected
    assert sanitize_endpoint_url("https://api.integ.groundlight.ai/device-api") == expected
    assert sanitize_endpoint_url("https://api.integ.groundlight.ai/device-api/") == expected

    expected = "http://localhost:8000/device-api"
    assert sanitize_endpoint_url("http://localhost:8000") == expected
    assert sanitize_endpoint_url("http://localhost:8000/") == expected
    assert sanitize_endpoint_url("http://localhost:8000/device-api") == expected
    assert sanitize_endpoint_url("http://localhost:8000/device-api/") == expected
