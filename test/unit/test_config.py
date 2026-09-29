import pytest
from groundlight.config import read_env_flag
from groundlight.internalapi import sanitize_endpoint_url

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


def test_read_env_flag(monkeypatch):
    """Unset returns the default. Only "1" and "0" are accepted, after stripping."""
    name = "GROUNDLIGHT_TEST_FLAG"
    monkeypatch.delenv(name, raising=False)
    assert read_env_flag(name, default=True) is True
    assert read_env_flag(name, default=False) is False

    monkeypatch.setenv(name, "1")
    assert read_env_flag(name, default=False) is True
    monkeypatch.setenv(name, " 0\n")
    assert read_env_flag(name, default=True) is False

    for raw in ("", "  ", "2", "true"):
        monkeypatch.setenv(name, raw)
        with pytest.raises(ValueError, match=name):
            read_env_flag(name, default=True)


def test_invalid_endpoint_config():
    for endpoint in BAD_ENDPOINTS:
        with pytest.raises(ValueError):
            sanitize_endpoint_url(endpoint)


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
