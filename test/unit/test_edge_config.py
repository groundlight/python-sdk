from datetime import datetime, timezone

import pytest
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
from model import Detector, DetectorTypeEnum

CUSTOM_REFRESH_RATE = 10.0
CUSTOM_AUDIT_RATE = 0.0


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
        "det_1",
        InferenceConfig(
            name="custom_config",
            always_return_edge_prediction=True,
            min_time_between_escalations=0.5,
        ),
    )
    detectors_config.add_detector(
        "det_2",
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
    detectors_config.add_detector("det_1", InferenceConfig(name="custom_config"))

    with pytest.raises(ValueError, match="different inference config named 'custom_config'"):
        detectors_config.add_detector(
            "det_2",
            InferenceConfig(name="custom_config", always_return_edge_prediction=True),
        )


def test_add_detector_rejects_duplicate_detector_id():
    """Rejects adding the same detector ID more than once."""
    detectors_config = DetectorsConfig()
    detectors_config.add_detector("det_1", DEFAULT)

    with pytest.raises(ValueError, match="already exists"):
        detectors_config.add_detector("det_1", DEFAULT)


def test_constructor_rejects_duplicate_detector_ids():
    """Rejects duplicated detector IDs in constructor input."""
    with pytest.raises(ValueError, match="Duplicate detector IDs"):
        DetectorsConfig(
            edge_inference_configs={"default": DEFAULT},
            detectors=[
                {"detector_id": "det_1", "edge_inference_config": "default"},
                {"detector_id": "det_1", "edge_inference_config": "default"},
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
        detectors=[{"detector_id": "det_1", "edge_inference_config": "default"}],
    )

    assert list(config.edge_inference_configs.keys()) == ["default"]
    assert [detector.detector_id for detector in config.detectors] == ["det_1"]


def test_constructor_rejects_undefined_inference_config_reference():
    """Rejects detector entries that reference missing inference configs."""
    with pytest.raises(ValueError, match="not defined"):
        DetectorsConfig(
            edge_inference_configs={},
            detectors=[{"detector_id": "det_1", "edge_inference_config": "does_not_exist"}],
        )


def test_edge_endpoint_config_add_detector_delegates_to_detectors_logic():
    """Adds detectors via EdgeEndpointConfig and preserves inferred config mapping."""
    config = EdgeEndpointConfig()
    config.add_detector("det_1", NO_CLOUD)
    config.add_detector("det_2", EDGE_ANSWERS_WITH_ESCALATION)
    config.add_detector("det_3", DEFAULT)

    assert [detector.detector_id for detector in config.detectors] == ["det_1", "det_2", "det_3"]
    assert set(config.edge_inference_configs.keys()) == {"no_cloud", "edge_answers_with_escalation", "default"}


def test_add_detector_accepts_detector_object():
    """Accepts Detector objects in add_detector."""
    config = EdgeEndpointConfig()
    config.add_detector(_make_detector("det_1"), DEFAULT)

    assert [detector.detector_id for detector in config.detectors] == ["det_1"]


def test_disabled_preset_can_be_used():
    """Allows assigning the DISABLED inference preset to a detector."""
    config = EdgeEndpointConfig()
    config.add_detector("det_1", DISABLED)

    assert [detector.edge_inference_config for detector in config.detectors] == ["disabled"]
    assert config.edge_inference_configs["disabled"] == DISABLED


def test_detectors_config_to_payload_shape():
    """Serializes detector-scoped payload with expected top-level keys."""
    detectors_config = DetectorsConfig()
    detectors_config.add_detector("det_1", DEFAULT)
    detectors_config.add_detector("det_2", NO_CLOUD)

    payload = detectors_config.to_payload()

    assert len(payload["detectors"]) == 2  # noqa: PLR2004
    assert set(payload["edge_inference_configs"].keys()) == {"default", "no_cloud"}


def test_model_dump_shape_for_edge_endpoint_config():
    """Serializes full edge endpoint config in flattened wire shape."""
    config = EdgeEndpointConfig(
        global_config=GlobalConfig(refresh_rate=CUSTOM_REFRESH_RATE, confident_audit_rate=CUSTOM_AUDIT_RATE)
    )
    config.add_detector("det_1", DEFAULT)
    config.add_detector("det_2", EDGE_ANSWERS_WITH_ESCALATION)
    config.add_detector("det_3", NO_CLOUD)

    payload = config.model_dump()

    assert payload["global_config"]["refresh_rate"] == CUSTOM_REFRESH_RATE
    assert payload["global_config"]["confident_audit_rate"] == CUSTOM_AUDIT_RATE
    assert len(payload["detectors"]) == 3  # noqa: PLR2004
    assert set(payload["edge_inference_configs"].keys()) == {"default", "edge_answers_with_escalation", "no_cloud"}


def test_inference_config_validation_errors():
    """Raises on invalid inference config flag combinations and values."""
    with pytest.raises(ValueError, match="disable_cloud_escalation"):
        InferenceConfig(name="bad", disable_cloud_escalation=True)

    with pytest.raises(ValueError, match="cannot be less than 0.0"):
        InferenceConfig(
            name="bad_escalation_interval",
            always_return_edge_prediction=True,
            min_time_between_escalations=-1.0,
        )
