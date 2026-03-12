"""Example of constructing an edge endpoint configuration programmatically."""

from groundlight import Groundlight
from groundlight.edge import DEFAULT, EDGE_WITH_ESCALATION, NO_CLOUD, EdgeInferenceConfig, RootEdgeConfig

gl = Groundlight()
detector1 = gl.get_detector("det_2z41nK0CyoFdWF6tEoB7DN5qwAx")
detector2 = gl.get_detector("det_2z41rs0Fo12LAk0oOZg0r4wR9Fn")
detector3 = gl.get_detector("det_2tYVTZrz8VLZhe94tjuPRl5rDeG")
detector4 = gl.get_detector("det_2sDfBz5xp6ZysB82kK7LfNYYSXx")
detector5 = gl.get_detector("det_2sDfGUP8cBt9Wrq0YFVLjVZhoI5")

config = RootEdgeConfig()

config.add_detector(detector1, NO_CLOUD)
config.add_detector(detector2, EDGE_WITH_ESCALATION)
config.add_detector(detector3, DEFAULT)

# Custom configs work alongside presets
my_custom_config = EdgeInferenceConfig(
    name="my_custom_config",
    always_return_edge_prediction=True,
    min_time_between_escalations=0.5,
)
detector_id = detector4.id
config.add_detector(detector_id, my_custom_config)

# Cannot reuse names on EdgeInferenceConfig
config_with_name_collision = EdgeInferenceConfig(name='default')
try:
    config.add_detector(detector5, config_with_name_collision)
except ValueError as e:
    print(e)

# Frozen -- mutation raises an error
try:
    NO_CLOUD.enabled = False
except Exception as e:
    print(e)

print(config.model_dump_json(indent=2))
