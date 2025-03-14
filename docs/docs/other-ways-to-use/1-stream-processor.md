# Low-Code Stream Processor

The [Groundlight Stream Processor](https://github.com/groundlight/stream) is a simple containerized application for processing video streams and submitting frames to Groundlight.

It supports a variety of input sources, including:
- Video devices (webcams)
- Video files (MP4, etc)
- RTSP streams
- HLS streams
- YouTube videos
- Image directories
- Image URLs

The Stream Processor can be combined with [Groundlight Alerts](../guide/10-alerts.md) to create a simple video analytics system. For example, you could use the Stream Processor to process a video stream from a security camera and send an alert when a person is detected.

## Prerequisites:
You will need:
1. A [Groundlight account](https://dashboard.groundlight.ai/)
2. An API token from the [Groundlight dashboard](https://dashboard.groundlight.ai/reef/my-account/api-tokens)
3. [Docker](https://www.docker.com/) installed on your system

Set your Groundlight API token as an environment variable:
```bash
export GROUNDLIGHT_API_TOKEN="<your-api-token>"
```

## Create a Detector via the Groundlight Dashboard
Once signed in to [the Groundlight dashboard](https://dashboard.groundlight.ai/), create a new detector by clicking the "Create New" button. Give your detector a name, a question, and a confidence threshold, then click "Save."

You will be redirected to the detector's page, where you can find the detector ID under the Setup tab. Note this ID for later use.

## Processing a Stream
Processing a stream is as easy as running a Docker container. For example, the following command will process a video file:
```bash
docker run -v /path/to/video:/videos groundlight/stream \
    -t "$GROUNDLIGHT_API_TOKEN" \
    -d “<your-detector-id>” \
    -s /videos/video.mp4 \
    -f 1
```
This will begin submitting frames from the video file to Groundlight. The `-f` flag specifies the frame rate in terms of frames per second. The container can be stopped by pressing `Ctrl+C`.

A variety of input sources are supported, including RTSP streams. To process an RTSP stream, run the following command:
```bash
docker run groundlight/stream \
    -t "$GROUNDLIGHT_API_TOKEN" \
    -d “<your-detector-id>” \
    -s "<your-rtsp-url>" \
    -f 0.5 \
    -v
```

This will begin submitting frames from the RTSP stream to Groundlight. The `-v` flag enables verbose logging.

If you only wish to submit frames to Groundlight when there is motion detected in the video stream, you can add the `-m` flag:
```bash
docker run groundlight/stream \
    -t "$GROUNDLIGHT_API_TOKEN" \
    -d “<your-detector-id>” \
    -s "<your-rtsp-url>" \
    -f 2 \
    -m
```

You may want the container to run in the background. To do this, add the `--detach` flag to the `docker run` command:
```bash
docker run --detach groundlight/stream \
    -t "$GROUNDLIGHT_API_TOKEN" \
    -d “<your-detector-id>” \
    -s "<your-rtsp-url>" \
    -f 2 \
    -m
```

:::tip
The Groundlight Stream Processor is lightweight and can be run on a Raspberry Pi or other low-power devices.
:::

## Combining with Groundlight Alerts
The Stream Processor submits frames to Groundlight, but it does not do anything with the results.

In order to build a useful alerting system, you can combine the Stream Processor with [Groundlight Alerts](../guide/10-alerts.md).
