---
id: esp32cam
title: "No-Code deployment on an ESP32 Camera Board"
sidebar_position: 1
---

# No-Code IoT Deployment

Groundlight supplies a tool for no-code deployment of a detector to an ESP32 Camera board. You can find it at [https://iot.groundlight.ai/espcam](https://iot.groundlight.ai/espcam).

## Easy Deployment

This tool is designed to make it as easy as possible to deploy your Groundlight detector on an ESP32 Camera Board. You can deploy your detector in just a few clicks.

1. Go to [https://iot.groundlight.ai/espcam](https://iot.groundlight.ai/espcam)
2. Plug your ESP32 Camera Board into your computer with a USB cable.
3. Click through the steps to upload your detector to your ESP32 Camera Board.
4. When prompted, allow your browser access to the serial port, so that it can program the device.

<img
src={require('/img/allow_serial_access.png').default}
alt="Dialog box in browser asking for serial port access"
width={"50%"}
/>

If you don't see a prompt like this, try using a current version of Chrome or another browser that supports Web Serial.

## Notification Options

The tool supports the following notification options for your deployed detector:

- Email
- SMS (With Twilio)
- Slack

## Multiple Supported Boards

Tested with the following boards. Many other ESP32 boards should work as well, but may require building the firmware from source and changing the IO pin definitions.

- M5Stack ESP32 PSRAM Timer Camera [[purchase here](https://shop.m5stack.com/products/esp32-psram-timer-camera-ov3660)]
- M5Stack ESP32 PSRAM Timer Camera X [[purchase here](https://shop.m5stack.com/products/esp32-psram-timer-camera-x-ov3660)]
- ESP32-CAM [[purchase here](https://www.amazon.com/s?k=ESP32-CAM&i=electronics)]
- SeeedStudio ESP32S3 Sense [[purchase here](https://www.seeedstudio.com/XIAO-ESP32S3-Sense-p-5639.html)]

<img
src={require('/img/m5stack_timer_camera.png').default}
alt="Example banner"
width={"25%"}
/>
<img
src={require('/img/m5stack_timer_camera_x.png').default}
alt="Example banner"
width={"25%"}
/>
<img
src={require('/img/esp32-cam.png').default}
alt="Example banner"
width={"25%"}
/>
<img
src={require('/img/xiao-esp32s3-sense.png').default}
alt="Example banner"
width={"25%"}
/>

## Source Code

The source code is written as an Arduino-based PlatformIO project for ESP32, and is available on GitHub at https://github.com/groundlight/esp32cam

If you need assistance or have questions about integrating Groundlight with Arduino, please consider opening an issue on the GitHub repository or reaching out to our [support team](mailto:support@groundlight.ai).
