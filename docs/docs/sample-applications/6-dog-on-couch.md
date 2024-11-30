# A Fun Example: Dog-on-Couch Detector

Here is a whimsical example of how you could use Groundlight in your home to keep your dog off the couch.  This document will guide you through creating a complete application. If the dog is detected on the couch, the application will play a pre-recorded sound over the computer's speakers, instructing the dog to get off the couch.  Be sure to record your own voice so that your dog pays attention to you.

## Requirements

- [Groundlight SDK](/docs/installation/) with Python 3.9 or higher
- A supported USB or network-connected camera
- A pre-recorded sound file (e.g., `get_off_couch.mp3`)
- A couch and a dog are recommended for proper end-to-end testing.

## Installation

Ensure you have Python 3.9 or higher installed, and then install the Groundlight SDK, OpenCV library, and other required libraries:

```bash
pip install groundlight opencv-python pillow pyaudio
```

## Creating the Application

1. First, log in to the [Groundlight dashboard](https://dashboard.groundlight.ai) and create an [API Token](https://dashboard.groundlight.ai/reef/my-account/api-tokens).

2. Next, we'll write the Python script for the application. Import the required libraries:

```python notest
import cv2
import pyaudio
import time
import wave
from PIL import Image
from groundlight import Groundlight, ApiException
```

3. Define a function to capture an image from the camera using OpenCV:

```python
def capture_image():
    cap = cv2.VideoCapture(0)

    ret, frame = cap.read()
    cap.release()

    if ret:
        # Convert to PIL image
        return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    else:
        return None
```

4. Define a function to play the pre-recorded sound:

```python
def play_sound(file_path):
    CHUNK = 1024
    wf = wave.open(file_path, 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)

    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

    p.terminate()
```

5. Write the main application loop:

```python notest
gl = Groundlight()

detector = gl.get_or_create_detector("Dog on Couch Detector")

while True:
    image = capture_image()
    if image:
        try:
            iq = gl.submit_image_query(image=image, detector=detector, wait=60)
            answer = iq.result.label
            if answer == "YES":
                print("Dog detected on the couch!")
                play_sound("get_off_couch.mp3")
        except ApiException as e:
            print(f"Error submitting image query: {e}")
    else:
        print("Failed to capture image")

    # Sleep for a minute before checking again
    time.sleep(60)
```

This application captures an image using the `capture_image` function, then submits it to the Groundlight API for analysis. If the dog is detected on the couch, it plays the pre-recorded sound using the `play_sound` function.

Save the script as `dog_on_couch_detector.py` and run it:

```bash
python dog_on_couch_detector.py
```
