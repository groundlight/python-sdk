from typing import Union

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


class EdgeInferenceConfig(BaseModel):
    """
    Configuration for edge inference on a specific detector.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., exclude=True, description="A unique name for this inference config preset.")
    enabled: bool = Field(  # TODO investigate and update the functionality of this option
        default=True, description="Whether the edge endpoint should accept image queries for this detector."
    )
    api_token: str | None = Field(
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


class RootEdgeConfig(BaseModel):
    """
    Root configuration for edge inference.
    """

    global_config: GlobalConfig = Field(default_factory=GlobalConfig)
    edge_inference_configs: dict[str, EdgeInferenceConfig] = Field(default_factory=dict)
    detectors: list[DetectorConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_inference_configs(self):
        for detector_config in self.detectors:
            if detector_config.edge_inference_config not in self.edge_inference_configs:
                raise ValueError(f"Edge inference config '{detector_config.edge_inference_config}' not defined.")
        return self

    def add_detector(
        self, detector: Union[str, Detector], edge_inference_config: Union[str, EdgeInferenceConfig]
    ) -> None:
        detector_id = detector.id if isinstance(detector, Detector) else detector
        if any(d.detector_id == detector_id for d in self.detectors):
            raise ValueError(f"A detector with ID '{detector_id}' already exists.")
        if isinstance(edge_inference_config, EdgeInferenceConfig):
            config = edge_inference_config
            existing = self.edge_inference_configs.get(config.name)
            if existing is None:
                self.edge_inference_configs[config.name] = config
            elif existing is not config:
                raise ValueError(
                    f"A different inference config named '{config.name}' is already registered."
                )
            config_name = config.name
        else:
            config_name = edge_inference_config
            if config_name not in self.edge_inference_configs:
                raise ValueError(
                    f"Edge inference config '{config_name}' not defined. "
                    f"Available configs: {list(self.edge_inference_configs.keys())}"
                )
        self.detectors.append(DetectorConfig(
            detector_id=detector_id,
            edge_inference_config=config_name,
        ))


# Preset inference configs matching the standard edge-endpoint defaults.
DEFAULT = EdgeInferenceConfig(name="default")
EDGE_WITH_ESCALATION = EdgeInferenceConfig(
    name="edge_with_escalation",
    always_return_edge_prediction=True,
    min_time_between_escalations=2.0,
)
NO_CLOUD = EdgeInferenceConfig(
    name="no_cloud",
    always_return_edge_prediction=True,
    disable_cloud_escalation=True,
)
DISABLED = EdgeInferenceConfig(name="disabled", enabled=False)
