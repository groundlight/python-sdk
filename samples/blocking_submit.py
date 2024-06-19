"""Example of how to wait for a confident result."""

import logging

from groundlight import Groundlight

logging.basicConfig(level=logging.DEBUG)

gl = Groundlight()

d = gl.get_or_create_detector(name="dog", query="is there a dog in the picture?")

print("Submitting image query")
iq = gl.submit_image_query(d, image="../test/assets/dog.jpeg", wait=30)
print(iq)
