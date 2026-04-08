from typing import Callable

from groundlight import ExperimentalApi

gl = ExperimentalApi()


def test_invalid_endpoint_config(detector_name: Callable):
    print(gl.make_generic_api_request(endpoint="/v1/me", method="GET"))
    print(gl.make_generic_api_request(endpoint="/v1/detectors", method="GET"))
    print(gl.make_generic_api_request(endpoint="/v1/detector-groups", method="POST", body={"name": detector_name()}))
