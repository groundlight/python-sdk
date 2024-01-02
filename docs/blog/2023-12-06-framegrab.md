---
title: Introducing Groundlight's FrameGrab Library
description: We would like to introduce you to the FrameGrab library. 
slug: introducing-framegrab
authors:
  - name: Tim Huff
    title: Engineering intern at Groundlight
    image_url: https://a-us.storyblok.com/f/1015187/1000x1000/06b25bf1a6/hufft.jpg
  - name: Blaise Munyampirwa
    title: Engineer at Groundlight
    image_url: https://a-us.storyblok.com/f/1015187/1000x1000/d12109465d/munyampirwab.jpg
  - name: Leo Dirac
    title: CTO and Co-founder at Groundlight
    image_url: https://a-us.storyblok.com/f/1015187/284x281/602a9c95c5/diracl.png
  - name: Tyler Romero 
    title: Senior Machine Learning Engineer
    image_url: https://a-us.storyblok.com/f/1015187/1000x1000/368053d79a/romerot.jpg 
  - name: Michael Vogelsong 
    title: Chief ML Scientist 
    image_url: https://a-us.storyblok.com/f/1015187/1000x1000/c87b9d30f4/vogelsongm.jpg


tags: [groundlight-extensions, framegrab]
image: /img/gl-icon400.png
hide_table_of_contents: false
---



At Groundlight, we continue to build infrastructure that allows our customers to easily use computer 
vision without a pre-existing dataset for industrial inspection, retail analytics, mobile robotics, and 
much more. We've built many features towards the goal of declarative computer vision, and today we are excited to 
introduce FrameGrab, a Python library designed to make it easy to grab frames from
cameras or streams. 

FrameGrab supports generic USB cameras, RTSP streams, Basler USB cameras, Basler GigE cameras, and Intel RealSense depth cameras. 

<!-- truncate -->


## Grabbing Camera Frames

Frame grabber objects are configured through YAML. The configuration combines the camera type, camera ID, and the camera
options. The YAML config contains many configurable features, but only `input_type` is required. Valid choices for 
`input_type` include 

* generic_usb
* rtsp
* realsense
* basler 

Here is an example of how to use the generic USB configuration 

```python notest
from framegrab import FrameGrabber 

config = """
name: Front Door Camera
input_type: generic_usb
id:
  serial_number: 23432570
options:
    resolution:
        height: 1080
        width: 1920
    zoom:
        digital: 1.5
"""

grabber = FrameGrabber.create_grabber_yaml(config)
frame = grabber.grab()

# Do real work with the frame 

# Finally release the grabber object 
grabber.release()

```

For the full set of configurable parameters, please refer to the [FrameGrab repository](https://github.com/groundlight/framegrab/tree/main).

## Multi-cam Configuration 

If you have multiple cameras of the same type plugged in, we recommend you include serial numbers in the YAML config to 
ensure proper pairing. The default pairing behavior is sequential (i.e., configurations will be paired with cameras in 
a sequential ordering). 

You can add serial numbers for multiple cameras like this

```yaml 
GL_CAMERAS: |
  - name: on robot arm
    input_type: realsense
    options: 
      depth:
        side_by_side: 1
      crop:
        relative:
          right: .8
  - name: conference room
      input_type: rtsp
      id: 
        rtsp_url: rtsp://admin:password@192.168.1.20/cam/realmonitor?channel=1&subtype=0
      options:
        crop:
          pixels:
            top: 350
            bottom: 1100
            left: 1100
            right: 2000
  - name: workshop
    input_type: generic_usb
    id:
      serial_number: B77D3A8F

```

## FrameGrab Autodiscovery Mode 

Among other features, FrameGrab also includes autodiscovery mode. This allows you to automatically connect to all cameras 
that are plugged into your machine (or discoverable on the network). Autodiscovery will load up default configurations 
for each camera. 

:::note

Please note that RTSP streams cannot be autodiscovered in this manner. RTSP URLs must be pre-specified in the 
configurations. 

:::

We recommend autodiscovery for simple applications where you don't need to set any special options on your cameras. 
It is also a convenient method for finding the serial numbers of your cameras in case they are not printed on them. 

Below is a short example of how to launch autodiscovery mode. 

```python notest
from framegrab import FrameGrabber

grabbers = FrameGrabber.autodiscover()

# Print some information about the discovered cameras
for grabber in grabbers.values():
    print(grabber.config)

    # Do real work 

    # Release the frame grabber object 
    grabber.release()

```


## Using FrameGrab for Motion Detection 

With this release, we also continue to support [motion detection](https://en.wikipedia.org/wiki/Motion_detection) via frame differencing, a 
fast algorithm for easily detecting motion in a sequence of frames. 

To use motion detection, initialize the MotionDetector instance with the desired percentage of pixels 
needed to change in an image for it to be flagged for motion and the minimum brightness change for each pixel for it 
to be considered changed. Here is a comprehensive example. 

```python notest
from framegrab import FrameGrabber, MotionDetector

config = {
    'input_type': 'webcam',
}
grabber = FrameGrabber.create_grabber(config)
motion_detector = MotionDetector(pct_threshold=motion_threshold, val_threshold=60)

while True:
    frame = grabber.grab()
    if frame is None:
        print("No frame captured!")
        continue

    if motion_detector.motion_detected(frame):
        print("Motion detected!")

```


## Conclusion 

Recent releases of FrameGrab add various easy to use features. We now support 
multiple camera types and continue to support motion detection. 

If you encounter any issues while using FrameGrab, please feel free to file an issue in our [GitHub repository](https://github.com/groundlight/framegrab)
and while there, review guidelines for [contributing](https://github.com/groundlight/framegrab#contributing) to this library. 
