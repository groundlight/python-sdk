"use strict";(self.webpackChunkcode_groundlight_ai=self.webpackChunkcode_groundlight_ai||[]).push([[5850],{3750:e=>{e.exports=JSON.parse('{"version":{"pluginId":"default","version":"current","label":"Next","banner":null,"badge":false,"noIndex":false,"className":"docs-version-current","isLast":true,"docsSidebars":{"tutorialSidebar":[{"type":"category","label":"Getting Started","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"Initial setup","href":"/python-sdk/docs/getting-started/initial-setup","docId":"getting-started/initial-setup","unlisted":false},{"type":"link","label":"Writing Queries","href":"/python-sdk/docs/getting-started/writing-queries","docId":"getting-started/writing-queries","unlisted":false},{"type":"link","label":"Using API Tokens","href":"/python-sdk/docs/getting-started/api-tokens","docId":"getting-started/api-tokens","unlisted":false}],"href":"/python-sdk/docs/getting-started/"},{"type":"category","label":"Installation","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"Installing on Linux","href":"/python-sdk/docs/installation/linux","docId":"installation/linux","unlisted":false},{"type":"link","label":"Installing on macOS","href":"/python-sdk/docs/installation/macos","docId":"installation/macos","unlisted":false},{"type":"link","label":"Installing on Windows","href":"/python-sdk/docs/installation/windows","docId":"installation/windows","unlisted":false},{"type":"link","label":"Optional libraries","href":"/python-sdk/docs/installation/optional-libraries","docId":"installation/optional-libraries","unlisted":false},{"type":"link","label":"Usage on Raspberry Pi","href":"/python-sdk/docs/installation/raspberry-pi","docId":"installation/raspberry-pi","unlisted":false},{"type":"link","label":"Usage on NVIDIA Jetson","href":"/python-sdk/docs/installation/nvidia-jetson","docId":"installation/nvidia-jetson","unlisted":false}],"href":"/python-sdk/docs/installation/"},{"type":"category","label":"Guide","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"Grabbing Images","href":"/python-sdk/docs/guide/grabbing-images","docId":"guide/grabbing-images","unlisted":false},{"type":"link","label":"Working with Detectors","href":"/python-sdk/docs/guide/working-with-detectors","docId":"guide/working-with-detectors","unlisted":false},{"type":"link","label":"Submitting Image Queries","href":"/python-sdk/docs/guide/submitting-image-queries","docId":"guide/submitting-image-queries","unlisted":false},{"type":"link","label":"Setting Confidence Thresholds","href":"/python-sdk/docs/guide/managing-confidence","docId":"guide/managing-confidence","unlisted":false},{"type":"link","label":"Handling Errors","href":"/python-sdk/docs/guide/handling-errors","docId":"guide/handling-errors","unlisted":false},{"type":"link","label":"Using Asynchronous Queries","href":"/python-sdk/docs/guide/async-queries","docId":"guide/async-queries","unlisted":false},{"type":"link","label":"Processing Images on the Edge","href":"/python-sdk/docs/guide/edge","docId":"guide/edge","unlisted":false},{"type":"link","label":"Configuring Alerts","href":"/python-sdk/docs/guide/alerts","docId":"guide/alerts","unlisted":false}],"href":"/python-sdk/docs/guide/"},{"type":"category","label":"Sample Applications","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"A Fun Example: Dog-on-Couch Detector","href":"/python-sdk/docs/sample-applications/dog-on-couch","docId":"sample-applications/dog-on-couch","unlisted":false},{"type":"link","label":"A Serious Example: Retail Analytics","href":"/python-sdk/docs/sample-applications/retail-analytics","docId":"sample-applications/retail-analytics","unlisted":false},{"type":"link","label":"A Quick Example: Live Stream Monitor","href":"/python-sdk/docs/sample-applications/streaming-with-alerts","docId":"sample-applications/streaming-with-alerts","unlisted":false},{"type":"link","label":"Industrial and Manufacturing Applications","href":"/python-sdk/docs/sample-applications/industrial","docId":"sample-applications/industrial","unlisted":false}],"href":"/python-sdk/docs/sample-applications/"},{"type":"category","label":"Alternative Deployment Options","collapsible":true,"collapsed":false,"items":[{"type":"link","label":"Low-Code Stream Processor","href":"/python-sdk/docs/other-ways-to-use/stream-processor","docId":"other-ways-to-use/stream-processor","unlisted":false},{"type":"link","label":"No-Code deployment on an ESP32 Camera Board","href":"/python-sdk/docs/other-ways-to-use/esp32cam","docId":"other-ways-to-use/esp32cam","unlisted":false},{"type":"link","label":"Low-Code Monitoring Notification Server","href":"/python-sdk/docs/other-ways-to-use/monitoring-notification-server","docId":"other-ways-to-use/monitoring-notification-server","unlisted":false}]},{"type":"link","label":"API Reference","href":"/python-sdk/docs/api-reference/","docId":"api-reference/redirect","unlisted":false}]},"docs":{"api-reference/redirect":{"id":"api-reference/redirect","title":"API Reference","description":"","sidebar":"tutorialSidebar"},"getting-started/api-tokens":{"id":"getting-started/api-tokens","title":"Using API Tokens","description":"API tokens authenticate your code to access Groundlight services. They look like api_2GdXMflhJ... and should be treated as sensitive credentials.","sidebar":"tutorialSidebar"},"getting-started/getting-started":{"id":"getting-started/getting-started","title":"Getting Started","description":"Computer Vision powered by Natural Language","sidebar":"tutorialSidebar"},"getting-started/initial-setup":{"id":"getting-started/initial-setup","title":"Initial setup","description":"In this guide, you will set up your development environment to interact with the Groundlight API using the Groundlight SDK. You will learn how to:","sidebar":"tutorialSidebar"},"getting-started/writing-queries":{"id":"getting-started/writing-queries","title":"Writing Queries","description":"Introduction","sidebar":"tutorialSidebar"},"guide/alerts":{"id":"guide/alerts","title":"Configuring Alerts","description":"Groundlight supports triggering alerts based on the results of image queries. Alerts can be configured to notify you when a specific condition is met.","sidebar":"tutorialSidebar"},"guide/async-queries":{"id":"guide/async-queries","title":"Using Asynchronous Queries","description":"Groundlight provides a simple interface for submitting asynchronous queries. This is useful for situations in which the thread or process or machine submitting image queries is not the same thread or machine that will be retrieving and using the results.","sidebar":"tutorialSidebar"},"guide/edge":{"id":"guide/edge","title":"Processing Images on the Edge","description":"If your account includes access to edge models, you can download and install them on your edge devices. This allows you to run Groundlight\'s ML models locally on your edge devices, reducing latency and increasing throughput. Additionally, inference requests handled on the edge are not counted towards your account\'s usage limits.","sidebar":"tutorialSidebar"},"guide/grabbing-images":{"id":"guide/grabbing-images","title":"Grabbing Images","description":"In order to analyze images with Groundlight, you first need to capture images from a camera or other image source. This guide will show you how to capture images from different sources and formats.","sidebar":"tutorialSidebar"},"guide/guide":{"id":"guide/guide","title":"Guide","description":"Groundlight provides a powerful \\"computer vision powered by natural language\\" system that enables you to build visual applications with minimal code. With Groundlight, you can quickly create applications for various use cases, from simple object detection to complex visual analysis.","sidebar":"tutorialSidebar"},"guide/handling-errors":{"id":"guide/handling-errors","title":"Handling Errors","description":"When building applications with the Groundlight SDK, you may encounter errors during API calls. This page covers how to handle such errors and build robust code that can gracefully handle exceptions.","sidebar":"tutorialSidebar"},"guide/managing-confidence":{"id":"guide/managing-confidence","title":"Setting Confidence Thresholds","description":"Introduction to Confidence Thresholds","sidebar":"tutorialSidebar"},"guide/submitting-image-queries":{"id":"guide/submitting-image-queries","title":"Submitting Image Queries","description":"Once you have created a Detector and captured an image, you can submit your image to Groundlight for analysis.","sidebar":"tutorialSidebar"},"guide/working-with-detectors":{"id":"guide/working-with-detectors","title":"Working with Detectors","description":"Explicitly create a new detector","sidebar":"tutorialSidebar"},"installation/installation":{"id":"installation/installation","title":"Installation Guide for Groundlight Python SDK","description":"The Groundlight Python SDK requires Python 3.9 or higher and can be installed on all major platforms. Follow the installation guide for your specific operating system or device below.","sidebar":"tutorialSidebar"},"installation/linux":{"id":"installation/linux","title":"Installing on Linux","description":"This guide will help you install the Groundlight SDK on Linux. The Groundlight SDK requires Python 3.9 or higher.","sidebar":"tutorialSidebar"},"installation/macos":{"id":"installation/macos","title":"Installing on macOS","description":"This guide will help you install the Groundlight SDK on macOS. The Groundlight SDK requires Python 3.9 or higher.","sidebar":"tutorialSidebar"},"installation/nvidia-jetson":{"id":"installation/nvidia-jetson","title":"Usage on NVIDIA Jetson","description":"This guide will help you install the Groundlight SDK on NVIDIA Jetson devices. The Groundlight SDK requires Python 3.9 or higher.","sidebar":"tutorialSidebar"},"installation/optional-libraries":{"id":"installation/optional-libraries","title":"Optional libraries","description":"Smaller is better!","sidebar":"tutorialSidebar"},"installation/raspberry-pi":{"id":"installation/raspberry-pi","title":"Usage on Raspberry Pi","description":"This guide will help you install the Groundlight SDK on Raspberry Pi. The Groundlight SDK requires Python 3.9 or higher.","sidebar":"tutorialSidebar"},"installation/windows":{"id":"installation/windows","title":"Installing on Windows","description":"This guide will help you install the Groundlight SDK on Windows. The Groundlight SDK requires Python 3.9 or higher.","sidebar":"tutorialSidebar"},"other-ways-to-use/esp32cam":{"id":"other-ways-to-use/esp32cam","title":"No-Code deployment on an ESP32 Camera Board","description":"Groundlight supplies a tool for no-code deployment of a detector to an ESP32 Camera board. You can find it at https://iot.groundlight.ai/espcam.","sidebar":"tutorialSidebar"},"other-ways-to-use/monitoring-notification-server":{"id":"other-ways-to-use/monitoring-notification-server","title":"Low-Code Monitoring Notification Server","description":"Groundlight\'s Monitoring Notification Server (MNS) is the easiest way to deploy your Groundlight detectors on a linux computer. All configuration is done through a web user interface, and no code development is required.","sidebar":"tutorialSidebar"},"other-ways-to-use/stream-processor":{"id":"other-ways-to-use/stream-processor","title":"Low-Code Stream Processor","description":"The Groundlight Stream Processor is a simple containerized application for processing video streams and submitting frames to Groundlight.","sidebar":"tutorialSidebar"},"sample-applications/dog-on-couch":{"id":"sample-applications/dog-on-couch","title":"A Fun Example: Dog-on-Couch Detector","description":"Here is a whimsical example of how you could use Groundlight in your home to keep your dog off the couch.  This document will guide you through creating a complete application. If the dog is detected on the couch, the application will play a pre-recorded sound over the computer\'s speakers, instructing the dog to get off the couch.  Be sure to record your own voice so that your dog pays attention to you.","sidebar":"tutorialSidebar"},"sample-applications/industrial":{"id":"sample-applications/industrial","title":"Industrial and Manufacturing Applications","description":"Modern natural language-based computer vision is transforming industrial and manufacturing applications by enabling more intuitive interaction with automation systems. Groundlight offers cutting-edge computer vision technology that can be seamlessly integrated into various industrial processes, enhancing efficiency, productivity, and quality control.","sidebar":"tutorialSidebar"},"sample-applications/retail-analytics":{"id":"sample-applications/retail-analytics","title":"A Serious Example: Retail Analytics","description":"Tracking utilization of a customer service counter","sidebar":"tutorialSidebar"},"sample-applications/sample-applications":{"id":"sample-applications/sample-applications","title":"Sample Applications","description":"Explore these example applications to see Groundlight\'s computer vision capabilities in action:","sidebar":"tutorialSidebar"},"sample-applications/streaming-with-alerts":{"id":"sample-applications/streaming-with-alerts","title":"A Quick Example: Live Stream Monitor","description":"A quick example to help you get started with monitoring live streams using the groundlight/stream container.","sidebar":"tutorialSidebar"}}}}')}}]);