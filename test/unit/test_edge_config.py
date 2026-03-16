import pytest
from groundlight.edge import (
    DEFAULT,
    EDGE_ANSWERS_WITH_ESCALATION,
    NO_CLOUD,
    DetectorsConfig,
    EdgeEndpointConfig,
    InferenceConfig,
)

ONE_DETECTOR = 1
TWO_DETECTORS = 2


def test_edge_endpoint_config_is_not_subclass_of_detectors_config():
    assert not issubclass(EdgeEndpointConfig, DetectorsConfig)


def test_add_detector_allows_equivalent_named_inference_config():
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

    assert len(detectors_config.detectors) == TWO_DETECTORS
    assert list(detectors_config.edge_inference_configs.keys()) == ["custom_config"]


def test_add_detector_rejects_different_named_inference_config():
    detectors_config = DetectorsConfig()
    detectors_config.add_detector("det_1", InferenceConfig(name="custom_config"))

    with pytest.raises(ValueError, match="different inference config named 'custom_config'"):
        detectors_config.add_detector(
            "det_2",
            InferenceConfig(name="custom_config", always_return_edge_prediction=True),
        )


def test_constructor_rejects_duplicate_detector_ids():
    with pytest.raises(ValueError, match="Duplicate detector IDs"):
        DetectorsConfig(
            edge_inference_configs={"default": DEFAULT},
            detectors=[
                {"detector_id": "det_1", "edge_inference_config": "default"},
                {"detector_id": "det_1", "edge_inference_config": "default"},
            ],
        )


def test_constructor_rejects_mismatched_inference_config_key_and_name():
    with pytest.raises(ValueError, match="must match InferenceConfig.name"):
        DetectorsConfig(
            edge_inference_configs={"default": InferenceConfig(name="not_default")},
            detectors=[],
        )


def test_constructor_accepts_matching_inference_config_key_and_name():
    config = DetectorsConfig(
        edge_inference_configs={"default": InferenceConfig(name="default")},
        detectors=[{"detector_id": "det_1", "edge_inference_config": "default"}],
    )

    assert list(config.edge_inference_configs.keys()) == ["default"]
    assert [detector.detector_id for detector in config.detectors] == ["det_1"]


def test_edge_endpoint_config_add_detector_delegates_to_detectors_logic():
    config = EdgeEndpointConfig()
    config.add_detector("det_1", NO_CLOUD)
    config.add_detector("det_2", EDGE_ANSWERS_WITH_ESCALATION)
    config.add_detector("det_3", DEFAULT)

    assert [detector.detector_id for detector in config.detectors] == ["det_1", "det_2", "det_3"]
    assert set(config.edge_inference_configs.keys()) == {"no_cloud", "edge_answers_with_escalation", "default"}


def test_from_detectors_config_copies_detector_data():
    detectors_config = DetectorsConfig()
    detectors_config.add_detector("det_1", DEFAULT)

    config = EdgeEndpointConfig.from_detectors_config(detectors_config)
    detectors_config.add_detector("det_2", DEFAULT)

    assert len(config.detectors) == ONE_DETECTOR
    assert len(detectors_config.detectors) == TWO_DETECTORS


def test_inference_config_validation_errors():
    with pytest.raises(ValueError, match="disable_cloud_escalation"):
        InferenceConfig(name="bad", disable_cloud_escalation=True)

    with pytest.raises(ValueError, match="cannot be less than 0.0"):
        InferenceConfig(
            name="bad_escalation_interval",
            always_return_edge_prediction=True,
            min_time_between_escalations=-1.0,
        )
