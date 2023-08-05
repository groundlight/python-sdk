"""
Command line interface for groundlight
"""
import fire
from groundlight import Groundlight


def submit_image(detector_id: str, image_path: str, endpoint: str = "https://api.groundlight.ai/"):
    """
    Submit an image for prediction
    """
    gl = Groundlight(endpoint=endpoint)
    print("Submitting image for prediction...")
    result = gl.submit_image_query(detector_id, image_path)
    print(result)


def main():
    fire.Fire(
        {
            "submit_image": submit_image,
        }
    )


if __name__ == "__main__":
    main()
