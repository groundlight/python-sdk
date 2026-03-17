from typing import Any, Optional, Union

from model import Detector
from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator
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

    # Keep shared presets immutable (DEFAULT/NO_CLOUD/etc.) so one mutation cannot globally change behavior.
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


class DetectorsConfig(BaseModel):
    """
    Detector and inference-config mappings for edge inference.
    """

    edge_inference_configs: dict[str, InferenceConfig] = Field(default_factory=dict)
    detectors: list[DetectorConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_inference_configs(self):
        """
        Validates detector config state.
        Raises ValueError if dict keys mismatch InferenceConfig.name, detector IDs are duplicated,
        or any detector references an undefined inference config.
        """
        for name, config in self.edge_inference_configs.items():
            if name != config.name:
                raise ValueError(f"Edge inference config key '{name}' must match InferenceConfig.name '{config.name}'.")

        seen_detector_ids = set()
        duplicate_detector_ids = set()
        for detector_config in self.detectors:
            detector_id = detector_config.detector_id
            if detector_id in seen_detector_ids:
                duplicate_detector_ids.add(detector_id)
            else:
                seen_detector_ids.add(detector_id)
        if duplicate_detector_ids:
            duplicates = ", ".join(sorted(duplicate_detector_ids))
            raise ValueError(f"Duplicate detector IDs are not allowed: {duplicates}.")

        for detector_config in self.detectors:
            if detector_config.edge_inference_config not in self.edge_inference_configs:
                raise ValueError(f"Edge inference config '{detector_config.edge_inference_config}' not defined.")
        return self

    def add_detector(self, detector: Union[str, Detector], edge_inference_config: InferenceConfig) -> None:
        """Add a detector with the given inference config. Accepts detector ID or Detector object."""
        detector_id = detector.id if isinstance(detector, Detector) else detector
        if any(existing.detector_id == detector_id for existing in self.detectors):
            raise ValueError(f"A detector with ID '{detector_id}' already exists.")

        existing = self.edge_inference_configs.get(edge_inference_config.name)
        if existing is None:
            self.edge_inference_configs[edge_inference_config.name] = edge_inference_config
        elif existing != edge_inference_config:
            raise ValueError(
                f"A different inference config named '{edge_inference_config.name}' is already registered."
            )

        self.detectors.append(
            DetectorConfig(detector_id=detector_id, edge_inference_config=edge_inference_config.name)
        )


    def to_payload(self) -> dict[str, Any]:
        """Return flattened detector payload used by edge-endpoint config HTTP APIs."""
        return {
            "edge_inference_configs": {
                name: config.model_dump() for name, config in self.edge_inference_configs.items()
            },
            "detectors": [detector.model_dump() for detector in self.detectors],
        }


class EdgeEndpointConfig(BaseModel):
    """
    Top-level edge endpoint configuration.
    """

    global_config: GlobalConfig = Field(default_factory=GlobalConfig)
    detectors_config: DetectorsConfig = Field(default_factory=DetectorsConfig)

    @property
    def edge_inference_configs(self) -> dict[str, InferenceConfig]:
        """Convenience accessor for detector inference config map."""
        return self.detectors_config.edge_inference_configs

    @property
    def detectors(self) -> list[DetectorConfig]:
        """Convenience accessor for detector assignments."""
        return self.detectors_config.detectors

    @model_serializer(mode="plain")
    def serialize(self):
        """Serialize to the flattened shape expected by edge-endpoint configs."""
        return {
            "global_config": self.global_config.model_dump(),
            **self.detectors_config.to_payload(),
        }

    def add_detector(self, detector: Union[str, Detector], edge_inference_config: InferenceConfig) -> None:
        """Add a detector with the given inference config. Accepts detector ID or Detector object."""
        self.detectors_config.add_detector(detector, edge_inference_config)


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
