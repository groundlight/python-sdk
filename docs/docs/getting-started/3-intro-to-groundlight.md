# Intro to Groundlight
Groundlight is a platform that allows you to create and deploy custom detectors to analyze streams of images. You can use Groundlight to build detectors that answer questions about images, such as "Is there a car in the leftmost parking space?" or "Is the door open?".

This guide introduce's Groundlight's capabilities.

## What you can do with Groundlight
Groundlight is designed to power industrial-grade computer vision applications.

Here is a non-exhaustive list of Groundlight's capabilities and common use cases:
### Image Classification
Groundlight can classify images into user-defined categories. For example, you can build a detector that classifies images of animals into "cat", "dog", or "other".

### Counting
Groundlight can count objects in images. For example, you can build a detector that counts the number of cars in a parking lot.

### Object Detection
Groundlight can detect objects in images. For example, you can build a detector that detects the presence and location of a person in an image.

### Text Recognition
Groundlight can recognize and extract text from images. For example, you can build a detector that reads the liscense plate of a truck or a code on the side of a shipping container.

## Enterprise Considerations
### Secure
[Soc II Type 2 compliant](https://www.groundlight.ai/blog/groundlight-ai-achieves-soc-2-type-2-compliance), Groundlight is designed to meet the highest security standards.

### Capable
Groundlight is designed to handle large volumes of images and provide real-time responses.

### Reliable
Groundlight has a sophisticated escalation system in place to ensure the accuracy of results. Specific confidence values are provided with each result.

### Cost conscious
Groundlight is designed to be cost-effective.

## Implementing a Groundlight Detector
1. Scope your use case.

1. Design and create your detector.
    - Define the question you want to answer and choose a corresponding answering mode (e.g. "yes/no", "classification", "counting", "object detection", "text recognition").
    - Choose a confidence threshold. Higher confidence thresholds will ensure a higher overall accuracy of the detector, but may result in higher costs. We recommend a confidence threshold of 0.9 for most common use-cases.

1. Submit images to your detector.
    - You can submit images to your detector using the Groundlight SDK. The SDK provides a simple interface to submit images and retrieve results.

1. Analyze the results and iterate.
    - Review the results of your detector and adjust the confidence threshold as needed. You can also adjust the question you are asking to improve the accuracy of the detector by resolving ambiguities.

1. Deploy your detector.
    - Once you are satisfied with the accuracy of your detector, you can begin consuming the results in your application. You can also deploy your detector to the Groundlight API for real-time processing.

## Start Building with Groundlight

Ready to get started with Groundlight? Here's how:
- Use the [Getting Started Guide](./getting-started.mdx) to make your first API call.
- Refer to the [API Reference](../api-reference/api-reference.md) for comprehensive details on the Groundlight API.
- Try the [Explore Page](https://dashboard.groundlight.ai/reef/explore/) to create a demo detector directly in your browser.
- Explore [sample applications built with Groundlight](../example-applications/sample-applications.md) for inspiration.