from groundlight import Groundlight

gl = Groundlight()
detectors = gl.list_detectors()
print(f"Found {detectors.count} detectors")
