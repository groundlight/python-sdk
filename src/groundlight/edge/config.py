from typing import Any, Optional, Union

import yaml
from model import Detector
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing_extensions import Self


class GlobalConfig(BaseModel):  # pylint: disable=too-few-public-methods
    """Global runtime settings for edge-endpoint behavior."""

    model_config = ConfigDict(extra="ignore")

    refresh_rate: float = Field(
        default=60.0,
        description="The interval (in seconds) at which the inference server checks for a new model binary update.",
    )
    confident_audit_rate: float = Field(
        default=1e-5,  # A detector running at 1 FPS = ~100,000 IQ/day, so 1e-5 is ~1 confident IQ/day audited
        description="The probability that any given confident prediction will be sent to the cloud for auditing.",
    )


class InferenceConfig(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Configuration for edge inference on a specific detector.
    """

    # Keep shared presets immutable (DEFAULT/NO_CLOUD/etc.) so one mutation cannot globally change behavior.
    model_config = ConfigDict(extra="ignore", frozen=True)

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


class DetectorConfig(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Configuration for a specific detector.
    """

    model_config = ConfigDict(extra="ignore")

    detector_id: str = Field(..., pattern=r"^det_[A-Za-z0-9]{27}$", description="Detector ID")
    edge_inference_config: str = Field(..., description="Config for edge inference.")


class ConfigBase(BaseModel):
    """Shared detector/inference configuration behavior for edge config models."""

    model_config = ConfigDict(extra="ignore")

    edge_inference_configs: dict[str, InferenceConfig] = Field(default_factory=dict)
    detectors: list[DetectorConfig] = Field(default_factory=list)

    @field_validator("edge_inference_configs", mode="before")
    @classmethod
    def hydrate_inference_config_names(
        cls, value: Optional[dict[str, Union[InferenceConfig, dict[str, Any]]]]
    ) -> dict[str, Union[InferenceConfig, dict[str, Any]]]:
        """Hydrate InferenceConfig.name from payload mapping keys."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            return value

        hydrated_configs: dict[str, Union[InferenceConfig, dict[str, Any]]] = {}
        for name, config in value.items():
            if isinstance(config, InferenceConfig):
                hydrated_configs[name] = config
                continue
            if not isinstance(config, dict):
                raise TypeError("Each edge inference config must be an object.")
            hydrated_configs[name] = {"name": name, **config}
        return hydrated_configs

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

        self.detectors.append(DetectorConfig(detector_id=detector_id, edge_inference_config=edge_inference_config.name))

    def to_payload(self) -> dict[str, Any]:
        """Return this config as a payload dictionary."""
        return self.model_dump()


class DetectorsConfig(ConfigBase):
    """
    Detector and inference-config mappings for edge inference.
    """


class EdgeEndpointConfig(ConfigBase):
    """
    Top-level edge endpoint configuration.
    """

    global_config: GlobalConfig = Field(default_factory=GlobalConfig)

    @classmethod
    def from_yaml(
        cls,
        filename: Optional[str] = None,
        yaml_str: Optional[str] = None,
    ) -> "EdgeEndpointConfig":
        """Create an EdgeEndpointConfig from a YAML filename or YAML string."""
        if filename is None and yaml_str is None:
            raise ValueError("Either filename or yaml_str must be provided.")
        if filename is not None and yaml_str is not None:
            raise ValueError("Only one of filename or yaml_str can be provided.")
        if filename is not None:
            if not filename.strip():
                raise ValueError("filename must be a non-empty path when provided.")
            with open(filename, "r", encoding="utf-8") as f:
                yaml_str = f.read()

        yaml_text = yaml_str or ""
        parsed = yaml.safe_load(yaml_text) or {}
        return cls.model_validate(parsed)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "EdgeEndpointConfig":
        """Construct an EdgeEndpointConfig from a payload dictionary."""
        return cls.model_validate(payload)


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
