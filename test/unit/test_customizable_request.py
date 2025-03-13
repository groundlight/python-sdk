from datetime import datetime

from groundlight import ExperimentalApi

gl = ExperimentalApi()


def test_invalid_endpoint_config():
    print(gl.make_generic_api_request(endpoint="/v1/me", method="GET"))
    print(gl.make_generic_api_request(endpoint="/v1/detectors", method="GET"))
    name = f"Test {datetime.utcnow()}"
    print(gl.make_generic_api_request(endpoint="/v1/detector-groups", method="POST", body={"name": name}))
