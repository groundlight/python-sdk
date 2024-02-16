---
title: "Building your first computer vision model just got easier"
slug: getting-started
authors:
  - name: Sunil Kumar
    title: Machine Learning Engineer
    image_url: https://a-us.storyblok.com/f/1015187/1000x1000/a265e322bd/kumars.jpg
tags: [Getting started, Groundlight Python SDK]
image: ./images/getting_started/cvme1.jpg
hide_table_of_contents: false
---

We're thrilled to announce a new [repository](https://github.com/groundlight/getting_started) that makes it incredibly easy for anyone to get started for free with Groundlight, a computer vision (CV) platform powered by natural language. This first steps guide is designed to walk you through setting up your first Groundlight detector to answer a simple question: "Is the door open?" Behind the scenes, Groundlight will automatically train and deploy a computer vision model that can answer this question in real time. With our escalation technology, you don't need to provide any labeled data - you get answers from your first image submission.

[![groundlight/getting_started - GitHub](https://gh-card.dev/repos/groundlight/getting_started.svg)](https://github.com/groundlight/getting_started)

<!-- truncate -->

## What is Groundlight?
Groundlight offers a truly modern take on computer vision, combining the best AI models with real-time human supervision in the cloud. Our Escalation Technology automatically chooses the best solution for your problem - whether that's a traditional CV model like an [EfficentNet](https://pytorch.org/hub/nvidia_deeplearningexamples_efficientnet/) on the edge, a powerful Visual LLM in the cloud, or a live sensible human monitor. The result is fairly incredible if you're used to the traditional `["gather data", "train model", "evaluate", "repeat"]` pattern of machine learning.  Instead, Groundlight empowers you to just phrase the visual question you want answered in English, send in images, and Groundlight provides confidence-calibrated answers.  At first, the answers will be slow and/or unconfident, but after not very many examples you're using a customized CV model trained just for your task.

<figure>
    <img src={require('./images/getting_started/escalation_diagram.jpg').default} />
    <figcaption>
    <small>
     Groundlight's escalation technology backs every question you ask Groundlight. Escalation ensures we find the best answer for your question, every time.
    </small>
    </figcaption>
</figure>

## What's Inside?
Our [getting started repository](https://github.com/groundlight/getting_started) provides an easy to understand Python codebase that you can run on any modern computer (including a Raspberry Pi). It captures images from a camera of your choice (by default your webcam) and uses Groundlight to continuously train and deploy a computer vision model that determines if your door is open or closed. Whether you're just starting out or a seasoned developer, this example is crafted to provide a smooth introduction to integrating Groundlight into your projects and provide a springboard for building advanced applications with Groundlight. 

The `main.py` file could hardly be simpler.  First you just initialize the camera and your Groundlight detector:

```python
camera = setup_camera()

gl = Groundlight()

query_text = "Is the door open? This includes if the door is only partially open."

detector_name = "door_open_detector"

detector = gl.get_or_create_detector(
    name=detector_name,
    query=query_text,
)
```

and then a simple infinite loop to send images from the camera to your detector:

```python
try:
    while True:
        image = camera.grab()

        image_query = gl.ask_ml(detector=detector, image=image)
        
        print(f"The answer to the query is {image_query.result.label.value}")

        sleep(10)
finally:
    camera.release()
```

## How do I get started?
Visit the [repository](https://github.com/groundlight/getting_started) and follow the steps in the `README`. After trying it out, we encourage you to modify the code to solve a real world problem you experience. Doing so should be as simple as changing the `query` you ask Groundlight. See the `Learning More - Additional Resources` section of the `README` for more information. If you want to learn more about the Groundlight Python SDK, which is used to power this repository, check out our [SDK](https://github.com/groundlight/python-sdk) or visit the [documentation](https://code.groundlight.ai/python-sdk/docs/getting-started).

## We're Here to Help!
Got questions? We're eager to assist! Reach out to us through email (support@groundlight.ai), or chat on the [Groundlight web app](https://app.groundlight.ai) - a Groundlight engineer or scientist is available to help every weekday during business hours.

We can't wait to see what you build with Groundlight! 
