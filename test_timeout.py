import groundlight

print(groundlight.__version__)

from PIL import Image

width, height = 100, 100
black_image = Image.new("RGB", (width, height), (0, 0, 0))

gl = groundlight.Groundlight()
print(gl.whoami())

input("Press Enter to continue...")

detector_id = "det_2X3FnKzmKbSb4K1wZA6GeJ8xrWJ"
iq = gl.submit_image_query(detector_id, black_image, inspection_id="")
print(iq)
