from typing import Optional, Union

from model import Detector
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Self


class GlobalConfig(BaseModel):
    refresh_rate: float = Field(
        default=60.0,
        description="The interval (in seconds) at which the inference server checks for a new model binary update.",
    )
    confident_audit_rate: float = Field(
        default=1e-5,  # A detector running at 1 FPS = ~100,000 IQ/day, so 1e-5 is ~1 confident IQ/day audited
        description="The probability that any given confident prediction will be sent to the cloud for auditing.",
    )


class InferenceConfig(BaseModel):
    """
    Configuration for edge inference on a specific detector.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., exclude=True, description="A unique name for this inference config preset.")
    enabled: bool = Field(
        default=True, description="Whether the edge endpoint should accept image queries for this detector."
    )
    api_token: Optional[str] = Field(
        default=None, description="API token used to fetch the inference model for this detector."
    )
    always_return_edge_prediction: bool = Field(
        default=False,
        description=(
            "Indicates if the edge-endpoint should always provide edge ML predictions, regardless of confidence. "
            "When this setting is true, whether or not the edge-endpoint should escalate low-confidence predictions "
            "to the cloud is determined by `disable_cloud_escalation`."
        ),
    )
    disable_cloud_escalation: bool = Field(
        default=False,
        description=(
            "Never escalate ImageQueries from the edge-endpoint to the cloud. "
            "Requires `always_return_edge_prediction=True`."
        ),
    )
    min_time_between_escalations: float = Field(
        default=2.0,
        description=(
            "The minimum time (in seconds) to wait between cloud escalations for a given detector. "
            "Cannot be less than 0.0. "
            "Only applies when `always_return_edge_prediction=True` and `disable_cloud_escalation=False`."
        ),
    )

    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        if self.disable_cloud_escalation and not self.always_return_edge_prediction:
            raise ValueError(
                "The `disable_cloud_escalation` flag is only valid when `always_return_edge_prediction` is set to True."
            )
        if self.min_time_between_escalations < 0.0:
            raise ValueError("`min_time_between_escalations` cannot be less than 0.0.")
        return self


class DetectorConfig(BaseModel):
    """
    Configuration for a specific detector.
    """

    detector_id: str = Field(..., description="Detector ID")
    edge_inference_config: str = Field(..., description="Config for edge inference.")


def _validate_detector_config_state(
    edge_inference_configs: dict[str, InferenceConfig], detectors: list[DetectorConfig]
) -> None:
    for name, config in edge_inference_configs.items():
        if name != config.name:
            raise ValueError(f"Edge inference config key '{name}' must match InferenceConfig.name '{config.name}'.")

    seen_detector_ids = set()
    duplicate_detector_ids = set()
    for detector_config in detectors:
        detector_id = detector_config.detector_id
        if detector_id in seen_detector_ids:
            duplicate_detector_ids.add(detector_id)
        else:
            seen_detector_ids.add(detector_id)
    if duplicate_detector_ids:
        duplicates = ", ".join(sorted(duplicate_detector_ids))
        raise ValueError(f"Duplicate detector IDs are not allowed: {duplicates}.")

    for detector_config in detectors:
        if detector_config.edge_inference_config not in edge_inference_configs:
            raise ValueError(f"Edge inference config '{detector_config.edge_inference_config}' not defined.")


def _add_detector_to_state(
    edge_inference_configs: dict[str, InferenceConfig],
    detectors: list[DetectorConfig],
    detector: Union[str, Detector],
    edge_inference_config: Union[str, InferenceConfig],
) -> DetectorConfig:
    detector_id = detector.id if isinstance(detector, Detector) else detector
    if any(existing.detector_id == detector_id for existing in detectors):
        raise ValueError(f"A detector with ID '{detector_id}' already exists.")
    if isinstance(edge_inference_config, InferenceConfig):
        config = edge_inference_config
        existing = edge_inference_configs.get(config.name)
        if existing is None:
            edge_inference_configs[config.name] = config
        elif existing != config:
            raise ValueError(f"A different inference config named '{config.name}' is already registered.")
        config_name = config.name
    else:
        config_name = edge_inference_config
        if config_name not in edge_inference_configs:
            raise ValueError(
                f"Edge inference config '{config_name}' not defined. "
                f"Available configs: {list(edge_inference_configs.keys())}"
            )

    detector_config = DetectorConfig(
        detector_id=detector_id,
        edge_inference_config=config_name,
    )
    detectors.append(detector_config)
    return detector_config


class DetectorsConfig(BaseModel):
    """
    Detector and inference-config mappings for edge inference.
    """

    edge_inference_configs: dict[str, InferenceConfig] = Field(default_factory=dict)
    detectors: list[DetectorConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_inference_configs(self):
        _validate_detector_config_state(self.edge_inference_configs, self.detectors)
        return self

    def add_detector(self, detector: Union[str, Detector], edge_inference_config: Union[str, InferenceConfig]) -> None:
        _add_detector_to_state(self.edge_inference_configs, self.detectors, detector, edge_inference_config)


class EdgeEndpointConfig(BaseModel):
    """
    Top-level edge endpoint configuration.
    """

    global_config: GlobalConfig = Field(default_factory=GlobalConfig)
    edge_inference_configs: dict[str, InferenceConfig] = Field(default_factory=dict)
    detectors: list[DetectorConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_inference_configs(self):
        _validate_detector_config_state(self.edge_inference_configs, self.detectors)
        return self

    def add_detector(self, detector: Union[str, Detector], edge_inference_config: Union[str, InferenceConfig]) -> None:
        _add_detector_to_state(self.edge_inference_configs, self.detectors, detector, edge_inference_config)

    @classmethod
    def from_detectors_config(
        cls, detectors_config: "DetectorsConfig", global_config: Optional[GlobalConfig] = None
    ) -> "EdgeEndpointConfig":
        copied_config = detectors_config.model_copy(deep=True)
        return cls(
            global_config=global_config or GlobalConfig(),
            edge_inference_configs=copied_config.edge_inference_configs,
            detectors=copied_config.detectors,
        )


# Preset inference configs matching the standard edge-endpoint defaults.
DEFAULT = InferenceConfig(name="default")
EDGE_ANSWERS_WITH_ESCALATION = InferenceConfig(
    name="edge_answers_with_escalation",
    always_return_edge_prediction=True,
    min_time_between_escalations=2.0,
)
NO_CLOUD = InferenceConfig(
    name="no_cloud",
    always_return_edge_prediction=True,
    disable_cloud_escalation=True,
)
DISABLED = InferenceConfig(name="disabled", enabled=False)
