from groundlight import Groundlight

gl = Groundlight(host="http://localhost:8000/device-api")
detectors = gl.retrieve_detectors().body
print(f"Found {detectors.count} detectors")
