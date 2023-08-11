"""
Command line interface for groundlight
"""
import fire
from groundlight import Groundlight
from typing import Optional


class GroundlightCLI:
    """
    A series of command line tools to quickly interact with the Groundlight API
    """

    def list_detectors(self, page=1, page_size=10, endpoint: str = "https://api.groundlight.ai/"):
        """
        Gets a page of detectors out of all detectors
        """
        gl = Groundlight(endpoint=endpoint)
        print("Getting detectors...")
        result = gl.list_detectors(page=page, page_size=page_size)
        print(result)

    def get_detector(self, detector_id: str, endpoint: str = "https://api.groundlight.ai/"):
        """
        Get a detector by ID
        Args:
            detector_id: The ID of the detector to get, will match the string returned by
        """
        gl = Groundlight(endpoint=endpoint)
        print("Getting detector...")
        result = gl.get_detector_by_name(detector_id)
        print(result)

    def submit_image(
        self,
        detector_id: str,
        image_path: str,
        endpoint: str = "https://api.groundlight.ai/",
    ):
        """
        Submit an image for prediction
        Args:
            detector_id: The ID of the detector to submit an image to, will match the string returned by
        """
        gl = Groundlight(endpoint=endpoint)
        print("Submitting image for prediction...")
        result = gl.submit_image_query(detector_id, image_path)
        print(result)


def main():
    fire.Fire(GroundlightCLI)


if __name__ == "__main__":
    main()
