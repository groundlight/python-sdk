from groundlight import ExperimentalApi

gl = ExperimentalApi()

print('Configuring Edge Endpoint...')
gl.configure_edge(
    edge_inference_configs={
        "tims_config": {
            "enabled": True,
            "always_return_edge_prediction": True,
            "disable_cloud_escalation": False,
            "min_time_between_escalations": 30.0,
        },
        "another_config": {
            "enabled": True,
            "always_return_edge_prediction": True,
            "disable_cloud_escalation": True,
            "min_time_between_escalations": 20.0,
        },    },
    detectors=[
        {"detector_id": "det_31WjVpvBiOmxUBzVqiOa3G2UgMV", "edge_inference_config": "tims_config"},
        {"detector_id": "det_346zU49rFpY9I7f1PiuzArYdTdJ", "edge_inference_config": "tims_config"},
        # {"detector_id": "det_398G23k3Dn6sRPVHbySHeyGLmai", "edge_inference_config": "tims_config"},
        # {"detector_id": "det_39oO6BR1IJjmLOjmWF3F4R4of4o", "edge_inference_config": "tims_config"},
        # {"detector_id": "det_2mWrXjFFSGcn2PYKakS7EfYfF3l", "edge_inference_config": "another_config"},
    ],
)
print("Configured Edge Endpoint successfully!")
