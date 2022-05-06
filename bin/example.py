from groundlight import Groundlight

gl = Groundlight(host="http://localhost:8000/device-api")
detectors = gl.list_detectors().body
print(f"Found {detectors.count} detectors")
