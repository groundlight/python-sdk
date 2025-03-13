from groundlight import ExperimentalApi
from datetime import datetime

gl = ExperimentalApi()

def test_invalid_endpoint_config():
    print(gl.make_generic_api_request("/v1/me", "GET"))
    print(gl.make_generic_api_request("/v1/detectors", "GET"))
    name = f"Test {datetime.utcnow()}"
    print(gl.make_generic_api_request("/v1/detector-groups", "POST", body={"name": name}))