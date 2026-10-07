from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
import requests
from groundlight import EdgeDetectorsNotReadyError, EdgeNotAvailableError, ExperimentalApi
from groundlight.edge import (
    DEFAULT,
    DISABLED,
    EDGE_ANSWERS_WITH_ESCALATION,
    NO_CLOUD,
    DetectorsConfig,
    EdgeEndpointConfig,
    GlobalConfig,
    InferenceConfig,
)
from groundlight.edge.api import DEFAULT_EDGE_READY_TIMEOUT_SEC
from model import Detector, DetectorTypeEnum
from pydantic import ValidationError


def _edge_api() -> ExperimentalApi:
    """Build an ExperimentalApi that never hits the network or token cache."""
    with patch.object(ExperimentalApi, "_verify_connectivity"):
        return ExperimentalApi(
            api_token="api_bootstrap_token_value_long_enough",
            enable_token_rotation=False,
        )


CUSTOM_REFRESH_RATE = 10.0
CUSTOM_AUDIT_RATE = 0.0
REFRESH_RATE_SECONDS = 15.0

# Mock detector IDs
DET_1 = "det_000000000000000000000000001"
DET_2 = "det_000000000000000000000000002"
DET_3 = "det_000000000000000000000000003"


def _make_detector(detector_id: str) -> Detector:
    return Detector(
        id=detector_id,
        type=DetectorTypeEnum.detector,
        created_at=datetime.now(timezone.utc),
        name="test detector",
        query="Is there a dog?",
        group_name="default",
        metadata=None,
        mode="BINARY",
        mode_configuration=None,
    )


def test_add_detector_allows_equivalent_named_inference_config():
    """Allows reusing the same named inference config with equivalent values."""
    detectors_config = DetectorsConfig()
    detectors_config.add_detector(
        DET_1,
        InferenceConfig(
            name="custom_config",
            always_return_edge_prediction=True,
            min_time_between_escalations=0.5,
        ),
    )
    detectors_config.add_detector(
        DET_2,
        InferenceConfig(
            name="custom_config",
            always_return_edge_prediction=True,
            min_time_between_escalations=0.5,
        ),
    )

    assert len(detectors_config.detectors) == 2  # noqa: PLR2004
    assert list(detectors_config.edge_inference_configs.keys()) == ["custom_config"]


def test_add_detector_rejects_different_named_inference_config():
    """Rejects conflicting inference config values under the same name."""
    detectors_config = DetectorsConfig()
    detectors_config.add_detector(DET_1, InferenceConfig(name="custom_config"))

    with pytest.raises(ValueError, match="different inference config named 'custom_config'"):
        detectors_config.add_detector(
            DET_2,
            InferenceConfig(name="custom_config", always_return_edge_prediction=True),
        )


def test_add_detector_rejects_duplicate_detector_id():
    """Rejects adding the same detector ID more than once."""
    detectors_config = DetectorsConfig()
    detectors_config.add_detector(DET_1, DEFAULT)

    with pytest.raises(ValueError, match="already exists"):
        detectors_config.add_detector(DET_1, DEFAULT)


def test_constructor_rejects_duplicate_detector_ids():
    """Rejects duplicated detector IDs in constructor input."""
    with pytest.raises(ValueError, match="Duplicate detector IDs"):
        DetectorsConfig(
            edge_inference_configs={"default": DEFAULT},
            detectors=[
                {"detector_id": DET_1, "edge_inference_config": "default"},
                {"detector_id": DET_1, "edge_inference_config": "default"},
            ],
        )


def test_constructor_rejects_mismatched_inference_config_key_and_name():
    """Rejects inference config dict keys that do not match config names."""
    with pytest.raises(ValueError, match="must match InferenceConfig.name"):
        DetectorsConfig(
            edge_inference_configs={"default": InferenceConfig(name="not_default")},
            detectors=[],
        )


def test_constructor_accepts_matching_inference_config_key_and_name():
    """Accepts constructor input when key/name pairs are consistent."""
    config = DetectorsConfig(
        edge_inference_configs={"default": InferenceConfig(name="default")},
        detectors=[{"detector_id": DET_1, "edge_inference_config": "default"}],
    )

    assert list(config.edge_inference_configs.keys()) == ["default"]
    assert [detector.detector_id for detector in config.detectors] == [DET_1]


def test_constructor_hydrates_inference_config_name_from_dict_key():
    """Hydrates inference config names from payload dict keys."""
    config = DetectorsConfig(
        edge_inference_configs={"default": {"enabled": True}},
        detectors=[{"detector_id": DET_1, "edge_inference_config": "default"}],
    )

    assert config.edge_inference_configs["default"].name == "default"


def test_constructor_rejects_detector_map_input():
    """Rejects detector maps and requires detector list payloads."""
    with pytest.raises(ValueError):
        DetectorsConfig(
            edge_inference_configs={"default": {"enabled": True}},
            detectors={DET_1: {"detector_id": DET_1, "edge_inference_config": "default"}},
        )


def test_constructor_rejects_undefined_inference_config_reference():
    """Rejects detector entries that reference missing inference configs."""
    with pytest.raises(ValueError, match="not defined"):
        DetectorsConfig(
            edge_inference_configs={},
            detectors=[{"detector_id": DET_1, "edge_inference_config": "does_not_exist"}],
        )


def test_edge_endpoint_config_add_detector_uses_shared_config_logic():
    """Adds detectors via EdgeEndpointConfig and preserves inferred config mapping."""
    config = EdgeEndpointConfig()
    config.add_detector(DET_1, NO_CLOUD)
    config.add_detector(DET_2, EDGE_ANSWERS_WITH_ESCALATION)
    config.add_detector(DET_3, DEFAULT)

    assert [detector.detector_id for detector in config.detectors] == [DET_1, DET_2, DET_3]
    assert set(config.edge_inference_configs.keys()) == {"no_cloud", "edge_answers_with_escalation", "default"}


def test_add_detector_accepts_detector_object():
    """Accepts Detector objects in add_detector."""
    config = EdgeEndpointConfig()
    config.add_detector(_make_detector(DET_1), DEFAULT)

    assert [detector.detector_id for detector in config.detectors] == [DET_1]


def test_disabled_preset_can_be_used():
    """Allows assigning the DISABLED inference preset to a detector."""
    config = EdgeEndpointConfig()
    config.add_detector(DET_1, DISABLED)

    assert [detector.edge_inference_config for detector in config.detectors] == ["disabled"]
    assert config.edge_inference_configs["disabled"] == DISABLED


def test_detectors_config_to_payload_shape():
    """Serializes detector-scoped payload with expected top-level keys."""
    detectors_config = DetectorsConfig()
    detectors_config.add_detector(DET_1, DEFAULT)
    detectors_config.add_detector(DET_2, NO_CLOUD)

    payload = detectors_config.to_payload()

    assert len(payload["detectors"]) == 2  # noqa: PLR2004
    assert set(payload["edge_inference_configs"].keys()) == {"default", "no_cloud"}


def test_edge_endpoint_config_accepts_top_level_payload_shape():
    """Accepts the top-level edge endpoint payload shape used by APIs."""
    config = EdgeEndpointConfig.model_validate({
        "global_config": {"refresh_rate": CUSTOM_REFRESH_RATE},
        "edge_inference_configs": {"default": {"enabled": True}},
        "detectors": [{"detector_id": DET_1, "edge_inference_config": "default"}],
    })

    assert config.global_config.refresh_rate == CUSTOM_REFRESH_RATE
    assert [detector.detector_id for detector in config.detectors] == [DET_1]


def test_edge_endpoint_config_from_yaml_accepts_yaml_text():
    """Parses edge-endpoint YAML text using EdgeEndpointConfig.from_yaml."""
    config = EdgeEndpointConfig.from_yaml(yaml_str=f"""
        global_config:
          refresh_rate: {REFRESH_RATE_SECONDS}
        edge_inference_configs:
          default:
            enabled: true
        detectors:
          - detector_id: {DET_1}
            edge_inference_config: default
        """)

    assert config.global_config.refresh_rate == REFRESH_RATE_SECONDS
    assert [detector.detector_id for detector in config.detectors] == [DET_1]


def test_edge_endpoint_config_from_yaml_accepts_filename(tmp_path):
    """Parses edge-endpoint YAML from a file path."""
    config_file = tmp_path / "edge-config.yaml"
    config_file.write_text(
        "global_config: {}\n"
        "edge_inference_configs:\n"
        "  default:\n"
        "    enabled: true\n"
        "detectors:\n"
        f"  - detector_id: {DET_1}\n"
        "    edge_inference_config: default\n"
    )
    config = EdgeEndpointConfig.from_yaml(filename=str(config_file))

    assert [detector.detector_id for detector in config.detectors] == [DET_1]


def test_edge_endpoint_config_from_yaml_requires_exactly_one_input():
    """Rejects missing input and mixed filename/yaml_str input."""
    with pytest.raises(ValueError, match="Either filename or yaml_str must be provided"):
        EdgeEndpointConfig.from_yaml()

    with pytest.raises(ValueError, match="Only one of filename or yaml_str can be provided"):
        EdgeEndpointConfig.from_yaml(filename="a.yaml", yaml_str="global_config: {}")

    with pytest.raises(ValueError, match="filename must be a non-empty path"):
        EdgeEndpointConfig.from_yaml(filename=" ")


def test_edge_endpoint_config_ignores_extra_fields_at_all_levels():
    """Unknown fields are silently ignored at every nesting level for forward compatibility."""
    config = EdgeEndpointConfig.model_validate({
        "global_config": {"refresh_rate": REFRESH_RATE_SECONDS, "unknown_global_field": "ignored"},
        "edge_inference_configs": {
            "default": {"enabled": True, "unknown_inference_field": 42},
        },
        "detectors": [
            {"detector_id": DET_1, "edge_inference_config": "default", "unknown_detector_field": [1, 2]},
        ],
        "unknown_top_level_field": True,
    })
    assert config.global_config.refresh_rate == REFRESH_RATE_SECONDS
    assert config.edge_inference_configs["default"].enabled is True
    assert config.detectors[0].detector_id == DET_1


def test_model_dump_shape_for_edge_endpoint_config():
    """Serializes full edge endpoint config in wire payload shape."""
    config = EdgeEndpointConfig(
        global_config=GlobalConfig(refresh_rate=CUSTOM_REFRESH_RATE, confident_audit_rate=CUSTOM_AUDIT_RATE)
    )
    config.add_detector(DET_1, DEFAULT)
    config.add_detector(DET_2, EDGE_ANSWERS_WITH_ESCALATION)
    config.add_detector(DET_3, NO_CLOUD)

    payload = config.to_payload()

    assert payload["global_config"]["refresh_rate"] == CUSTOM_REFRESH_RATE
    assert payload["global_config"]["confident_audit_rate"] == CUSTOM_AUDIT_RATE
    assert len(payload["detectors"]) == 3  # noqa: PLR2004
    assert set(payload["edge_inference_configs"].keys()) == {"default", "edge_answers_with_escalation", "no_cloud"}


def test_edge_endpoint_config_from_payload_round_trip():
    """Round-trips edge endpoint config through payload helpers."""
    config = EdgeEndpointConfig()
    config.add_detector(DET_1, DEFAULT)
    config.add_detector(DET_2, NO_CLOUD)

    payload = config.to_payload()
    reconstructed = EdgeEndpointConfig.from_payload(payload)

    assert reconstructed == config


def test_edge_endpoint_config_from_payload_accepts_literal_payload():
    """Constructs EdgeEndpointConfig from a literal payload dictionary."""
    payload = {
        "global_config": {"refresh_rate": REFRESH_RATE_SECONDS},
        "edge_inference_configs": {"default": {"enabled": True}},
        "detectors": [{"detector_id": DET_1, "edge_inference_config": "default"}],
    }

    config = EdgeEndpointConfig.from_payload(payload)

    assert config.global_config.refresh_rate == REFRESH_RATE_SECONDS
    assert config.edge_inference_configs["default"].name == "default"
    assert [detector.detector_id for detector in config.detectors] == [DET_1]


def test_inference_config_validation_errors():
    """Raises on invalid inference config flag combinations and values."""
    with pytest.raises(ValueError, match="disable_cloud_escalation"):
        InferenceConfig(name="bad", disable_cloud_escalation=True)

    with pytest.raises(ValidationError, match="greater_than"):
        InferenceConfig(
            name="bad_escalation_interval",
            always_return_edge_prediction=True,
            min_time_between_escalations=-1.0,
        )


def test_confident_audit_rate_allows_zero():
    """Zero is a valid confident_audit_rate (disables auditing)."""
    gc = GlobalConfig(confident_audit_rate=0.0)
    assert gc.confident_audit_rate == 0.0


def test_edge_get_config_parses_response():
    """gl.edge.get_config() parses the HTTP response into an EdgeEndpointConfig."""
    payload = {
        "global_config": {"refresh_rate": REFRESH_RATE_SECONDS},
        "edge_inference_configs": {"default": {"enabled": True}},
        "detectors": [{"detector_id": DET_1, "edge_inference_config": "default"}],
    }

    mock_response = Mock()
    mock_response.json.return_value = payload
    mock_response.raise_for_status = Mock()

    gl = _edge_api()
    with patch("requests.request", return_value=mock_response) as mock_request:
        config = gl.edge.get_config()

    mock_request.assert_called_once()
    assert isinstance(config, EdgeEndpointConfig)
    assert config.global_config.refresh_rate == REFRESH_RATE_SECONDS
    assert config.edge_inference_configs["default"].name == "default"
    assert [d.detector_id for d in config.detectors] == [DET_1]


def test_edge_set_config_sends_payload_and_polls():
    """gl.edge.set_config() PUTs the config then polls readiness until all detectors are ready."""
    config = EdgeEndpointConfig()
    config.add_detector(DET_1, DEFAULT)

    put_response = Mock()
    put_response.raise_for_status = Mock()

    readiness_response = Mock()
    readiness_response.json.return_value = {DET_1: {"ready": True}}
    readiness_response.raise_for_status = Mock()

    get_response = Mock()
    get_response.json.return_value = config.to_payload()
    get_response.raise_for_status = Mock()

    def route_request(method, url, **kwargs):
        if method == "PUT":
            return put_response
        if "/edge-detector-readiness" in url:
            return readiness_response
        return get_response

    gl = _edge_api()
    with patch("requests.request", side_effect=route_request) as mock_request:
        result = gl.edge.set_config(config)

    assert _http_methods(mock_request) == ["PUT", "GET", "GET"]
    assert _http_paths(mock_request)[0].endswith("/edge-config")
    assert _http_paths(mock_request)[1].endswith("/edge-detector-readiness")
    assert _http_paths(mock_request)[2].endswith("/edge-config")

    assert isinstance(result, EdgeEndpointConfig)
    assert [d.detector_id for d in result.detectors] == [DET_1]


def _http_methods(mock_request) -> list[str]:
    return [call.args[0] for call in mock_request.call_args_list]


def _http_paths(mock_request) -> list[str]:
    return [call.args[1] for call in mock_request.call_args_list]


def test_edge_apply_config_puts_without_polling_readiness():
    """gl.edge.apply_config() PUTs the document and does not poll readiness."""
    config = EdgeEndpointConfig()
    config.add_detector(DET_1, DEFAULT)

    put_response = Mock()
    put_response.raise_for_status = Mock()

    gl = _edge_api()
    with patch("requests.request", return_value=put_response) as mock_request:
        assert gl.edge.apply_config(config) is None

    assert _http_methods(mock_request) == ["PUT"]
    assert mock_request.call_args.args[1].endswith("/edge-config")
    assert mock_request.call_args.kwargs["json"]["detectors"][0]["detector_id"] == DET_1


def test_edge_apply_config_rejects_none():
    """gl.edge.apply_config(None) fails without a request."""
    gl = _edge_api()
    with patch("requests.request") as mock_request:
        with pytest.raises(TypeError, match="apply_config requires"):
            gl.edge.apply_config(None)  # type: ignore[arg-type]
    mock_request.assert_not_called()


def test_edge_wait_detectors_does_not_put_config():
    """gl.edge.wait_detectors() polls readiness and never PUTs /edge-config."""
    not_ready = Mock()
    not_ready.json.return_value = {DET_1: {"ready": False}}
    not_ready.raise_for_status = Mock()
    ready = Mock()
    ready.json.return_value = {DET_1: {"ready": True}}
    ready.raise_for_status = Mock()

    gl = _edge_api()
    with (
        patch("groundlight.edge.api.time.sleep"),
        patch("requests.request", side_effect=[not_ready, ready]) as mock_request,
    ):
        gl.edge.wait_detectors([DET_1], timeout_sec=30)

    assert all(path.endswith("/edge-detector-readiness") for path in _http_paths(mock_request))
    assert "PUT" not in _http_methods(mock_request)


def test_edge_wait_detectors_empty_list_is_noop():
    """An empty detector list returns immediately with no HTTP."""
    gl = _edge_api()
    with patch("requests.request") as mock_request:
        gl.edge.wait_detectors([])
        gl.edge.wait_detectors([], timeout_sec=0.001)
    mock_request.assert_not_called()


def test_edge_wait_detectors_times_out_when_detectors_stay_down():
    """Timeout names only the detectors that never became ready."""
    readiness = Mock()
    readiness.json.return_value = {DET_1: {"ready": True}, DET_2: {"ready": False}}
    readiness.raise_for_status = Mock()

    times = iter([100.0, 100.0, 101.0])
    gl = _edge_api()
    with (
        patch("groundlight.edge.api.time.sleep"),
        patch("groundlight.edge.api.time.time", side_effect=lambda: next(times)),
        patch("requests.request", return_value=readiness),
    ):
        with pytest.raises(EdgeDetectorsNotReadyError, match=DET_2) as exc_info:
            gl.edge.wait_detectors([DET_1, DET_2], timeout_sec=0.5)

    assert DET_1 not in str(exc_info.value)
    assert "configuration" not in str(exc_info.value).lower()
    assert isinstance(exc_info.value, TimeoutError)


def test_edge_wait_detectors_nonpositive_timeout_uses_default_budget():
    """timeout_sec <= 0 means DEFAULT_EDGE_READY_TIMEOUT_SEC, not skip-the-wait."""
    readiness = Mock()
    readiness.json.return_value = {DET_1: {"ready": False}}
    readiness.raise_for_status = Mock()

    clock = {"t": 0.0}

    def fake_time():
        return clock["t"]

    def fake_sleep(seconds):
        clock["t"] += seconds

    gl = _edge_api()
    with (
        patch("groundlight.edge.api.time.sleep", side_effect=fake_sleep),
        patch("groundlight.edge.api.time.time", side_effect=fake_time),
        patch("requests.request", return_value=readiness),
    ):
        with pytest.raises(EdgeDetectorsNotReadyError):
            gl.edge.wait_detectors([DET_1], timeout_sec=0)

    # One poll per second over the default 600s budget (sleep min(1, remaining)).
    assert clock["t"] == pytest.approx(DEFAULT_EDGE_READY_TIMEOUT_SEC)


def test_edge_set_config_empty_detectors_skips_readiness():
    """A config with no detectors PUTs then GETs, without polling readiness."""
    config = EdgeEndpointConfig()
    put_response = Mock()
    put_response.raise_for_status = Mock()
    get_response = Mock()
    get_response.json.return_value = config.to_payload()
    get_response.raise_for_status = Mock()

    def route_request(method, url, **kwargs):
        if method == "PUT":
            return put_response
        if method == "GET" and url.endswith("/edge-config"):
            return get_response
        raise AssertionError(f"unexpected {method} {url}")

    gl = _edge_api()
    with patch("requests.request", side_effect=route_request) as mock_request:
        result = gl.edge.set_config(config)

    assert _http_methods(mock_request) == ["PUT", "GET"]
    assert [d.detector_id for d in result.detectors] == []


def test_edge_get_detector_readiness():
    """gl.edge.get_detector_readiness() returns a dict mapping detector IDs to booleans."""
    mock_response = Mock()
    mock_response.json.return_value = {
        DET_1: {"ready": True},
        DET_2: {"ready": False},
    }
    mock_response.raise_for_status = Mock()

    gl = _edge_api()
    with patch("requests.request", return_value=mock_response):
        readiness = gl.edge.get_detector_readiness()

    assert readiness == {DET_1: True, DET_2: False}


def test_edge_get_upstream_endpoint():
    """gl.edge.get_upstream_endpoint() returns the upstream origin from the edge's /edge-info route."""
    upstream = "https://api.groundlight.dev.axon.com"
    mock_response = Mock()
    mock_response.json.return_value = {"upstream_endpoint": upstream}
    mock_response.raise_for_status = Mock()

    gl = ExperimentalApi()
    with patch("requests.request", return_value=mock_response) as mock_request:
        result = gl.edge.get_upstream_endpoint()

    assert result == upstream
    mock_request.assert_called_once()
    assert mock_request.call_args.args[:2] == ("GET", f"{gl.edge_base_url()}/edge-info")


def test_edge_get_upstream_endpoint_not_available():
    """gl.edge.get_upstream_endpoint() raises EdgeNotAvailableError when the route returns 404."""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=Mock(status_code=404))

    gl = ExperimentalApi()
    with patch("requests.request", return_value=mock_response):
        with pytest.raises(EdgeNotAvailableError):
            gl.edge.get_upstream_endpoint()


@pytest.mark.parametrize(
    "json_result",
    [
        {"unexpected": "shape"},
        ["not", "an", "object"],
        ValueError("Expecting value: line 1 column 1 (char 0)"),
    ],
    ids=["missing_key", "not_an_object", "not_json"],
)
def test_edge_get_upstream_endpoint_unexpected_response(json_result):
    """gl.edge.get_upstream_endpoint() raises EdgeNotAvailableError when a 200 response has an unexpected body."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    if isinstance(json_result, Exception):
        mock_response.json.side_effect = json_result
    else:
        mock_response.json.return_value = json_result

    gl = ExperimentalApi()
    with patch("requests.request", return_value=mock_response):
        with pytest.raises(EdgeNotAvailableError):
            gl.edge.get_upstream_endpoint()


def test_edge_wait_detectors_missing_id_is_not_ready():
    """A detector absent from the readiness map is treated as not ready."""
    readiness = Mock()
    readiness.json.return_value = {DET_1: {"ready": True}}
    readiness.raise_for_status = Mock()

    times = iter([100.0, 100.0, 101.0])
    gl = _edge_api()
    with (
        patch("groundlight.edge.api.time.sleep"),
        patch("groundlight.edge.api.time.time", side_effect=lambda: next(times)),
        patch("requests.request", return_value=readiness),
    ):
        with pytest.raises(EdgeDetectorsNotReadyError, match=DET_2):
            gl.edge.wait_detectors([DET_1, DET_2], timeout_sec=0.5)


def test_edge_apply_config_propagates_http_error():
    """apply_config does not swallow a failed PUT."""
    config = EdgeEndpointConfig()
    config.add_detector(DET_1, DEFAULT)

    failed = Mock()
    failed.status_code = 500
    failed.raise_for_status.side_effect = requests.HTTPError(response=failed)

    gl = _edge_api()
    with patch("requests.request", return_value=failed):
        with pytest.raises(requests.HTTPError):
            gl.edge.apply_config(config)


def test_edge_set_config_timeout_still_puts():
    """When wait times out, set_config has already PUTed the document."""
    config = EdgeEndpointConfig()
    config.add_detector(DET_1, DEFAULT)

    put_response = Mock()
    put_response.raise_for_status = Mock()
    readiness = Mock()
    readiness.json.return_value = {DET_1: {"ready": False}}
    readiness.raise_for_status = Mock()

    methods: list[str] = []

    def route_request(method, url, **kwargs):
        methods.append(method)
        if method == "PUT":
            return put_response
        if "/edge-detector-readiness" in url:
            return readiness
        raise AssertionError(f"unexpected {method} {url}")

    times = iter([100.0, 100.0, 101.0])
    gl = _edge_api()
    with (
        patch("groundlight.edge.api.time.sleep"),
        patch("groundlight.edge.api.time.time", side_effect=lambda: next(times)),
        patch("requests.request", side_effect=route_request),
    ):
        with pytest.raises(EdgeDetectorsNotReadyError, match="configuration has been applied") as exc_info:
            gl.edge.set_config(config, timeout_sec=0.5)

    assert methods[0] == "PUT"
    assert "GET" in methods
    assert "configuration has been applied" in str(exc_info.value).lower()


def test_edge_wait_detectors_positive_timeout_does_not_stretch_to_default():
    """A positive timeout_sec is the budget, not DEFAULT_EDGE_READY_TIMEOUT_SEC."""
    readiness = Mock()
    readiness.json.return_value = {DET_1: {"ready": False}}
    readiness.raise_for_status = Mock()

    clock = {"t": 0.0}

    def fake_time():
        return clock["t"]

    def fake_sleep(seconds):
        clock["t"] += seconds

    gl = _edge_api()
    with (
        patch("groundlight.edge.api.time.sleep", side_effect=fake_sleep),
        patch("groundlight.edge.api.time.time", side_effect=fake_time),
        patch("requests.request", return_value=readiness),
    ):
        with pytest.raises(EdgeDetectorsNotReadyError):
            gl.edge.wait_detectors([DET_1], timeout_sec=2.0)

    assert clock["t"] == pytest.approx(2.0)
    assert clock["t"] < DEFAULT_EDGE_READY_TIMEOUT_SEC
