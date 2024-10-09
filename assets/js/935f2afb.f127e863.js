"use strict";(self.webpackChunkweb=self.webpackChunkweb||[]).push([[8581],{5610:i=>{i.exports=JSON.parse('{"pluginId":"default","version":"current","label":"Next","banner":null,"badge":false,"noIndex":false,"className":"docs-version-current","isLast":true,"docsSidebars":{"tutorialSidebar":[{"type":"category","label":"Getting Started","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"API Tokens","href":"/python-sdk/docs/getting-started/api-tokens","docId":"getting-started/api-tokens","unlisted":false},{"type":"link","label":"Writing Queries","href":"/python-sdk/docs/getting-started/writing-queries","docId":"getting-started/writing-queries","unlisted":false},{"type":"link","label":"A Serious Example: Retail Analytics","href":"/python-sdk/docs/getting-started/retail-analytics","docId":"getting-started/retail-analytics","unlisted":false},{"type":"link","label":"A Fun Example: Dog-on-Couch Detector","href":"/python-sdk/docs/getting-started/dog-on-couch","docId":"getting-started/dog-on-couch","unlisted":false},{"type":"link","label":"A Quick Example: Live Stream Alert","href":"/python-sdk/docs/getting-started/streaming","docId":"getting-started/streaming","unlisted":false}],"href":"/python-sdk/docs/getting-started/"},{"type":"category","label":"Building Applications","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"Sample Applications","href":"/python-sdk/docs/building-applications/sample-applications","docId":"building-applications/sample-applications","unlisted":false},{"type":"link","label":"Grabbing Images","href":"/python-sdk/docs/building-applications/grabbing-images","docId":"building-applications/grabbing-images","unlisted":false},{"type":"link","label":"Working with Detectors","href":"/python-sdk/docs/building-applications/working-with-detectors","docId":"building-applications/working-with-detectors","unlisted":false},{"type":"link","label":"Confidence Levels","href":"/python-sdk/docs/building-applications/managing-confidence","docId":"building-applications/managing-confidence","unlisted":false},{"type":"link","label":"Handling Server Errors","href":"/python-sdk/docs/building-applications/handling-errors","docId":"building-applications/handling-errors","unlisted":false},{"type":"link","label":"Asynchronous Queries","href":"/python-sdk/docs/building-applications/async-queries","docId":"building-applications/async-queries","unlisted":false},{"type":"link","label":"Using Groundlight on the Edge","href":"/python-sdk/docs/building-applications/edge","docId":"building-applications/edge","unlisted":false},{"type":"link","label":"Industrial and Manufacturing Applications","href":"/python-sdk/docs/building-applications/industrial","docId":"building-applications/industrial","unlisted":false}],"href":"/python-sdk/docs/building-applications/"},{"type":"category","label":"Installation","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"Installing on Linux","href":"/python-sdk/docs/installation/linux","docId":"installation/linux","unlisted":false},{"type":"link","label":"Installing on macOS","href":"/python-sdk/docs/installation/macos","docId":"installation/macos","unlisted":false},{"type":"link","label":"Installing on Windows","href":"/python-sdk/docs/installation/windows","docId":"installation/windows","unlisted":false},{"type":"link","label":"Installing on Raspberry Pi","href":"/python-sdk/docs/installation/raspberry-pi","docId":"installation/raspberry-pi","unlisted":false},{"type":"link","label":"Installing on NVIDIA Jetson","href":"/python-sdk/docs/installation/nvidia-jetson","docId":"installation/nvidia-jetson","unlisted":false},{"type":"link","label":"Optional libraries","href":"/python-sdk/docs/installation/optional-libraries","docId":"installation/optional-libraries","unlisted":false},{"type":"link","label":"Monitoring Notification Server","href":"/python-sdk/docs/installation/monitoring-notification-server","docId":"installation/monitoring-notification-server","unlisted":false}],"href":"/python-sdk/docs/installation/"},{"type":"link","label":"IoT","href":"/python-sdk/docs/iot/","docId":"iot/esp32cam","unlisted":false},{"type":"link","label":"API Reference","href":"/python-sdk/docs/api-reference/","docId":"api-reference/redirect","unlisted":false}]},"docs":{"api-reference/redirect":{"id":"api-reference/redirect","title":"API Reference","description":"","sidebar":"tutorialSidebar"},"building-applications/async-queries":{"id":"building-applications/async-queries","title":"Asynchronous Queries","description":"Groundlight provides a simple interface for submitting asynchronous queries. This is useful for times in which the thread or process or machine submitting image queries is not the same thread or machine that will be retrieving and using the results. For example, you might have a forward deployed robot or camera that submits image queries to Groundlight, and a separate server that retrieves the results and takes action based on them. We will refer to these two machines as the submitting machine and the retrieving machine.","sidebar":"tutorialSidebar"},"building-applications/building-applications":{"id":"building-applications/building-applications","title":"Building Applications","description":"Groundlight provides a powerful \\"computer vision powered by natural language\\" system that enables you to build visual applications with minimal code. With Groundlight, you can quickly create applications for various use cases, from simple object detection to complex visual analysis.","sidebar":"tutorialSidebar"},"building-applications/edge":{"id":"building-applications/edge","title":"Using Groundlight on the Edge","description":"If your account has access to edge models, you can download and install them to your edge devices.","sidebar":"tutorialSidebar"},"building-applications/grabbing-images":{"id":"building-applications/grabbing-images","title":"Grabbing Images","description":"Groundlight\'s SDK accepts images in many popular formats, including PIL, OpenCV, and numpy arrays.","sidebar":"tutorialSidebar"},"building-applications/handling-errors":{"id":"building-applications/handling-errors","title":"Handling Server Errors","description":"When building applications with the Groundlight SDK, you may encounter server errors during API calls. This page covers how to handle such errors and build robust code that can gracefully handle exceptions.","sidebar":"tutorialSidebar"},"building-applications/industrial":{"id":"building-applications/industrial","title":"Industrial and Manufacturing Applications","description":"Modern natural language-based computer vision is transforming industrial and manufacturing applications by enabling more intuitive interaction with automation systems. Groundlight offers cutting-edge computer vision technology that can be seamlessly integrated into various industrial processes, enhancing efficiency, productivity, and quality control.","sidebar":"tutorialSidebar"},"building-applications/managing-confidence":{"id":"building-applications/managing-confidence","title":"Confidence Levels","description":"Groundlight gives you a simple way to control the trade-off of latency against accuracy. The longer you can wait for an answer to your image query, the better accuracy you can get. In particular, if the ML models are unsure of the best response, they will escalate the image query to more intensive analysis with more complex models and real-time human monitors as needed. Your code can easily wait for this delayed response. Either way, these new results are automatically trained into your models so your next queries will get better results faster.","sidebar":"tutorialSidebar"},"building-applications/sample-applications":{"id":"building-applications/sample-applications","title":"Sample Applications","description":"Explore these GitHub repositories to see examples of Groundlight-powered applications:","sidebar":"tutorialSidebar"},"building-applications/working-with-detectors":{"id":"building-applications/working-with-detectors","title":"Working with Detectors","description":"Explicitly create a new detector","sidebar":"tutorialSidebar"},"getting-started/api-tokens":{"id":"getting-started/api-tokens","title":"API Tokens","description":"About API Tokens","sidebar":"tutorialSidebar"},"getting-started/dog-on-couch":{"id":"getting-started/dog-on-couch","title":"A Fun Example: Dog-on-Couch Detector","description":"Here is a whimsical example of how you could use Groundlight in your home to keep your dog off the couch.  This document will guide you through creating a complete application. If the dog is detected on the couch, the application will play a pre-recorded sound over the computer\'s speakers, instructing the dog to get off the couch.  Be sure to record your own voice so that your dog pays attention to you.","sidebar":"tutorialSidebar"},"getting-started/getting-started":{"id":"getting-started/getting-started","title":"Getting Started","description":"Computer Vision powered by Natural Language","sidebar":"tutorialSidebar"},"getting-started/retail-analytics":{"id":"getting-started/retail-analytics","title":"A Serious Example: Retail Analytics","description":"Tracking utilization of a customer service counter","sidebar":"tutorialSidebar"},"getting-started/streaming":{"id":"getting-started/streaming","title":"A Quick Example: Live Stream Alert","description":"A quick example to get used to setting up detectors and asking good questions: set up a monitor on a live stream.","sidebar":"tutorialSidebar"},"getting-started/writing-queries":{"id":"getting-started/writing-queries","title":"Writing Queries","description":"Introduction","sidebar":"tutorialSidebar"},"installation/installation":{"id":"installation/installation","title":"Installation","description":"Welcome to the Groundlight SDK installation guide. In this guide, you\'ll find step-by-step instructions on how to install and set up the Groundlight SDK on various platforms.","sidebar":"tutorialSidebar"},"installation/linux":{"id":"installation/linux","title":"Installing on Linux","description":"This guide will help you install the Groundlight SDK on Linux. The Groundlight SDK requires Python 3.8 or higher.","sidebar":"tutorialSidebar"},"installation/macos":{"id":"installation/macos","title":"Installing on macOS","description":"This guide will help you install the Groundlight SDK on macOS. The Groundlight SDK requires Python 3.8 or higher.","sidebar":"tutorialSidebar"},"installation/monitoring-notification-server":{"id":"installation/monitoring-notification-server","title":"Monitoring Notification Server","description":"This is the easiest way to deploy your Groundlight detectors on a linux computer. All configuration is done through a web user interface, and no code development is required.","sidebar":"tutorialSidebar"},"installation/nvidia-jetson":{"id":"installation/nvidia-jetson","title":"Installing on NVIDIA Jetson","description":"This guide will help you install the Groundlight SDK on NVIDIA Jetson devices. The Groundlight SDK requires Python 3.8 or higher.","sidebar":"tutorialSidebar"},"installation/optional-libraries":{"id":"installation/optional-libraries","title":"Optional libraries","description":"Smaller is better!","sidebar":"tutorialSidebar"},"installation/raspberry-pi":{"id":"installation/raspberry-pi","title":"Installing on Raspberry Pi","description":"This guide will help you install the Groundlight SDK on Raspberry Pi. The Groundlight SDK requires Python 3.8 or higher.","sidebar":"tutorialSidebar"},"installation/windows":{"id":"installation/windows","title":"Installing on Windows","description":"This guide will help you install the Groundlight SDK on Windows. The Groundlight SDK requires Python 3.8 or higher.","sidebar":"tutorialSidebar"},"iot/esp32cam":{"id":"iot/esp32cam","title":"Setting up an ESP32 Camera Board","description":"Groundlight supplies a tool for no-code deployment of a detector to an ESP32 Camera board. You can find it at https://iot.groundlight.ai/espcam.","sidebar":"tutorialSidebar"}}}')}}]);