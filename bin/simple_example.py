from groundlight import Groundlight

gl = Groundlight()
detectors = gl.list_detectors().body
print(f"Found {detectors.count} detectors")
