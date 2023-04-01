# Groundlight

## Computer vision made simple

Build a working computer vision system in just 5 lines of python:

```python
{!> ../samples/main_usage.py!}
```

### How does it work?

Your images are first analyzed by machine learning (ML) models which are automatically trained on your data. If those models have high enough confidence, that's your answer. But if the models are unsure, then the images are progressively escalated to more resource-intensive analysis methods up to real-time human review. So what you get is a computer vision system that starts working right away without even needing to first gather and label a dataset. At first it will operate with high latency, because people need to review the image queries. But over time, the ML systems will learn and improve so queries come back faster with higher confidence.

_Note: The SDK is currently in "beta" phase. Interfaces are subject to change in future versions._

## Getting Started

1.  Install the `groundlight` SDK. Requires python version 3.7 or higher. See [prerequisites](#Prerequisites).

    ```shell
    $ pip3 install groundlight
    ```

1.  To access the API, you need an API token. You can create one on the
    [groundlight web app](https://app.groundlight.ai/reef/my-account/api-tokens). The API token
    should be stored securely. You can use it directly in your code to initialize the SDK like:

    ```python
    gl = Groundlight(api_token="<YOUR_API_TOKEN>")
    ```

    This is an easy way to get started, but is NOT a best practice. Please do not commit your API Token to version control! Instead we recommend setting the `GROUNDLIGHT_API_TOKEN` environment variable outside your code so that the SDK can find it automatically.

    ```bash
    $ export GROUNDLIGHT_API_TOKEN=api_2GdXMflhJi6L_example
    ```

1.  Create a python file.

    ```python title="hello.py"
    {!> ../samples/main_usage.py!}
    ```

1.  Run it!

    ```shell
    $ python hello.py
    ```
