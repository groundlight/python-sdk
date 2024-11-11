# A Quick Example: Live Stream Alert

A quick example to get used to setting up detectors and asking good questions: set up a monitor on a live stream.

## Requirements

- [Groundlight SDK](/docs/installation/) with Python 3.8 or higher
- The video ID of a YouTube live stream you'd like to monitor

## Installation

Ensure you have Python 3.8 or higher installed, and then install the Groundlight SDK and OpenCV library:

```bash
# MacOS
brew install ffmpeg

# Ubuntu/Fedora linux
sudo apt install -y ffmpeg

pip install groundlight pillow ffmpeg yt-dlp typer
```

## Creating the Application

1. Save this command as a shell script `get_latest_frame.sh`:

```
#!/bin/bash

ffmpeg -i "$(yt-dlp -g $1 | head -n 1)" -vframes 1 last.jpg -y
```

This will download the most recent frame from a YouTube live stream and save it to a local file `last.jpg`.

2. Ensure that the script has execute permissions. You can add execute permissions using the following command:

```
chmod +x get_latest_frame.sh
```

3. Log in to the [Groundlight dashboard](https://dashboard.groundlight.ai) and create an [API Token](https://dashboard.groundlight.ai/reef/my-account/api-tokens).

4. Next, we'll write the Python script for the application.

```python notest
import os
import subprocess
import typer
from groundlight import Groundlight
from PIL import Image


def main(*, video_id: str = None, detector_name: str = None, query: str = None, confidence: float = 0.75, wait: int = 60):
    """
    Run the script to get the stream's last frame as a subprocess, and submit result as an image query to a Groundlight detector
    :param video_id: Video ID of the YouTube live stream (the URLs have the form https://www.youtube.com/watch?v=<VIDEO_ID>)
    :param detector_name: Name for your Groundlight detector
    :param query: Question you want to ask of the stream (we will alert on the answer of NO)
    """
    gl = Groundlight()
    detector = gl.get_or_create_detector(name=detector_name, query=query, confidence_threshold=confidence)

    while True:
        p = subprocess.run(["./get_latest_frame.sh", video_id])
        if p.returncode != 0:
            raise RuntimeError(f"Could not get image from video ID: {video_id}. Process exited with return code {p.returncode}.")

        image = Image.open("last.jpg").convert("RGB")
        response = gl.submit_image_query(detector=detector, image=image, wait=wait)

        if response.result.label == "NO":
            os.system("say 'Alert!'") # this may not work on all operating systems


if __name__ == "__main__":
    typer.run(main)

```

5. Save the script as `streaming_alert.py` in the same directory as `get_latest_frame.sh` above and run it:

```bash
python streaming_alert.py --video-id=<VIDEO_ID> --detector-name=<DETECTOR_NAME> --query=<QUERY IN QUOTATION MARKS>
```
