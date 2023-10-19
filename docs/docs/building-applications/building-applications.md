# Building Applications

Groundlight provides a powerful "computer vision powered by natural language" system that enables you to build visual applications with minimal code. With Groundlight, you can quickly create applications for various use cases, from simple object detection to complex visual analysis.

In this page, we'll introduce you to some sample applications built using Groundlight and provide links to more detailed guides on various topics.

## Sample Applications

Explore these GitHub repositories to see examples of Groundlight-powered applications:

### Groundlight Stream Processor

Repository: [https://github.com/groundlight/stream](https://github.com/groundlight/stream)

The Groundlight Stream Processor is an easy-to-use Docker container for analyzing RTSP streams or common USB-based cameras. You can run it with a single Docker command, such as:

```bash
docker run stream:local --help
```

### Arduino ESP32 Camera Sample App

Repository: [https://github.com/groundlight/esp32cam](https://github.com/groundlight/esp32cam)

This sample application allows you to build a working AI vision detector using an inexpensive WiFi camera. With a cost of under $10, you can create a powerful and affordable AI vision system.

### Raspberry Pi

Repository: [https://github.com/groundlight/raspberry-pi-door-lock](https://github.com/groundlight/raspberry-pi-door-lock)

This sample application demonstrates how to set up a Raspberry Pi-based door lock system. The application monitors a door and sends a notification if the door is observed to be unlocked during non-standard business hours.

### Industrial and Manufacturing Applications

Groundlight can be used to [apply modern natural-language-based computer vision to industrial and manufacturing applications](/docs/building-applications/industrial).

## Further Reading

For more in-depth guides on various aspects of building applications with Groundlight, check out the following pages:
- **[Grabbing images](1-grabbing-images.md)**: Understand the intricacies of how to submit images from various input sources to Groundlight.
- **[Working with detectors](2-working-with-detectors.md)**: Learn how to create, configure, and use detectors in your Groundlight-powered applications.
- **[Confidence levels](3-managing-confidence.md)**: Master how to control the trade-off of latency against accuracy by configuring the desired confidence level for your detectors.
- **[Handling server errors](4-handling-errors.md)**: Understand how to handle and troubleshoot HTTP errors that may occur while using Groundlight.
- **[Asynchronous queries](5-async-queries.md)**: Groundlight makes it easy to submit asynchronous queries. Learn how to submit queries asynchronously and retrieve the results later.
- **[Using Groundlight on the edge](6-edge.md)**: Discover how to deploy Groundlight in edge computing environments for improved performance and reduced latency.
- **[Industrial applications](7-industrial.md)**: Learn how to apply modern natural-language-based computer vision to your industrial and manufacturing applications.
  
By exploring these resources and sample applications, you'll be well on your way to building powerful visual applications using Groundlight's computer vision and natural language capabilities.


