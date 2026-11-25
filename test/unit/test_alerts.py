"""Unit tests for ExperimentalApi.create_alert and add_alert_verdict, with the HTTP transport mocked."""

import json
from datetime import datetime, timezone
from typing import Iterator
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
from groundlight import ExperimentalApi
from groundlight_openapi_client.exceptions import ApiException
from groundlight_openapi_client.rest import RESTClientObject
from model import Alert, AlertVerdictEnum, AlertVerdictSourceEnum, Verdict

_FAKE_API_TOKEN = "api_fake_test_token_xx"
_ALERT_ID = "0b6f1d2e-4c1a-4f1e-9a43-6a3f9c2d8e71"
_TRIGGERED_AT = datetime(2026, 11, 16, 14, 3, 12, tzinfo=timezone.utc)
_DECIDED_AT = datetime(2026, 11, 16, 14, 3, 15, tzinfo=timezone.utc)

_ALERT_JSON = {
    "id": _ALERT_ID,
    "triggered_at": "2026-11-16T14:03:12Z",
    "image_query_count": 2,
    "lens_id": "person_down_lens",
    "camera_id": "cam-north-entrance",
    "device_id": "4a1f3c90b27e",
    "created_at": "2026-11-16T14:03:13Z",
}
_VERDICT_JSON = {
    "alert_id": _ALERT_ID,
    "source": "VLM",
    "verdict": "FALSE_ALARM",
    "rationale": "The person is kneeling to tie a shoe.",
    "decided_at": "2026-11-16T14:03:15Z",
    "reviewer": "gpt-5.4",
    "created_at": "2026-11-16T14:03:16Z",
}


@pytest.fixture(name="gl")
def experimental_fixture(monkeypatch) -> Iterator[ExperimentalApi]:
    """Build an ExperimentalApi without live connectivity or token-rotation network calls."""
    monkeypatch.setenv("GROUNDLIGHT_API_TOKEN", _FAKE_API_TOKEN)
    with (
        patch("groundlight.client.TokenManager", return_value=MagicMock()),
        patch.object(ExperimentalApi, "_verify_connectivity", return_value=None),
    ):
        yield ExperimentalApi(endpoint="http://test-server/device-api/")


def _transport(captured: dict, response: dict, status: int = 201):
    """Return a fake RESTClientObject.request that records the request and returns ``response``."""

    def fake_request(self, method, url, **kwargs):  # noqa: ANN001
        captured["method"] = method
        captured["url"] = url
        captured["body"] = kwargs.get("body")
        resp = MagicMock()
        resp.status = status
        resp.reason = "Conflict" if status == 409 else "OK"  # noqa: PLR2004
        resp.data = json.dumps(response).encode()
        resp.getheader = lambda name, default=None: ("application/json" if name.lower() == "content-type" else default)
        resp.getheaders = lambda: {"Content-Type": "application/json"}
        if status >= 400:  # noqa: PLR2004
            raise ApiException(http_resp=resp)
        return resp

    return fake_request


def _create_alert(gl: ExperimentalApi, **overrides) -> Alert:
    """Call create_alert with valid defaults, overridden by ``overrides``."""
    kwargs = {
        "alert_id": _ALERT_ID,
        "triggered_at": _TRIGGERED_AT,
        "image_query_count": 2,
        "lens_id": "person_down_lens",
        "camera_id": "cam-north-entrance",
        "device_id": "4a1f3c90b27e",
        **overrides,
    }
    return gl.create_alert(**kwargs)


def _add_verdict(gl: ExperimentalApi, **overrides) -> Verdict:
    """Call add_alert_verdict with valid defaults, overridden by ``overrides``."""
    kwargs = {
        "alert": _ALERT_ID,
        "source": AlertVerdictSourceEnum.VLM,
        "verdict": AlertVerdictEnum.FALSE_ALARM,
        "decided_at": _DECIDED_AT,
        **overrides,
    }
    return gl.add_alert_verdict(**kwargs)


def test_create_alert_sends_body_and_returns_alert(gl: ExperimentalApi):
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _transport(captured, _ALERT_JSON)):
        alert = _create_alert(gl, alert_id=UUID(_ALERT_ID))

    assert captured["method"] == "POST"
    assert captured["url"].endswith("/device-api/v1/alerts")
    assert captured["body"] == {
        "id": _ALERT_ID,
        "triggered_at": "2026-11-16T14:03:12+00:00",
        "image_query_count": 2,
        "lens_id": "person_down_lens",
        "camera_id": "cam-north-entrance",
        "device_id": "4a1f3c90b27e",
    }
    assert isinstance(alert, Alert)
    assert alert.id == UUID(_ALERT_ID)
    assert alert.triggered_at == _TRIGGERED_AT


def test_create_alert_returns_existing_alert_on_200(gl: ExperimentalApi):
    with patch.object(RESTClientObject, "request", _transport({}, _ALERT_JSON, status=200)):
        assert _create_alert(gl).id == UUID(_ALERT_ID)


def test_create_alert_conflict_raises_api_exception(gl: ExperimentalApi):
    with patch.object(RESTClientObject, "request", _transport({}, {"detail": "conflict"}, status=409)):
        with pytest.raises(ApiException) as exc_info:
            _create_alert(gl)
    assert exc_info.value.status == 409  # noqa: PLR2004


def test_create_alert_rejects_naive_datetime(gl: ExperimentalApi):
    with pytest.raises(ValueError, match="triggered_at must be timezone-aware"):
        _create_alert(gl, triggered_at=datetime(2026, 11, 16, 14, 3, 12))


def test_create_alert_rejects_non_uuid_id(gl: ExperimentalApi):
    with pytest.raises(ValueError):
        _create_alert(gl, alert_id="alert-1")


def test_add_alert_verdict_sends_enums_and_returns_verdict(gl: ExperimentalApi):
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _transport(captured, _VERDICT_JSON)):
        verdict = _add_verdict(gl, rationale="The person is kneeling to tie a shoe.", reviewer="gpt-5.4")

    assert captured["method"] == "POST"
    assert captured["url"].endswith(f"/device-api/v1/alerts/{_ALERT_ID}/verdicts")
    assert captured["body"] == {
        "source": "VLM",
        "verdict": "FALSE_ALARM",
        "decided_at": "2026-11-16T14:03:15+00:00",
        "rationale": "The person is kneeling to tie a shoe.",
        "reviewer": "gpt-5.4",
    }
    assert isinstance(verdict, Verdict)
    assert verdict.source is AlertVerdictSourceEnum.VLM
    assert verdict.verdict is AlertVerdictEnum.FALSE_ALARM


def test_add_alert_verdict_accepts_strings_and_alert_object(gl: ExperimentalApi):
    with patch.object(RESTClientObject, "request", _transport({}, _ALERT_JSON)):
        alert = _create_alert(gl)
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _transport(captured, _VERDICT_JSON)):
        _add_verdict(gl, alert=alert, source="VLM", verdict="CONFIRMED")

    assert captured["url"].endswith(f"/v1/alerts/{_ALERT_ID}/verdicts")
    assert captured["body"] == {"source": "VLM", "verdict": "CONFIRMED", "decided_at": "2026-11-16T14:03:15+00:00"}


@pytest.mark.parametrize("overrides", [{"source": "OPERATOR"}, {"verdict": "MAYBE"}, {"alert": "alert-1"}])
def test_add_alert_verdict_rejects_invalid_values(gl: ExperimentalApi, overrides: dict):
    with pytest.raises(ValueError):
        _add_verdict(gl, **overrides)


def test_add_alert_verdict_rejects_naive_datetime(gl: ExperimentalApi):
    with pytest.raises(ValueError, match="decided_at must be timezone-aware"):
        _add_verdict(gl, decided_at=datetime(2026, 11, 16, 14, 3, 15))
