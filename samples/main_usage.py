from groundlight import Groundlight

gl = Groundlight()
d = gl.get_or_create_detector(name="door", query="Is the door open?")
image_query = gl.submit_image_query(detector=d, image=jpeg_img)
print(f"The answer is {image_query.result}")
