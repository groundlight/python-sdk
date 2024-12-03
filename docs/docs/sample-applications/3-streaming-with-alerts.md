# A Quick Example: Live Stream Monitor

A quick example to help you get started with monitoring live streams using the [groundlight/stream](../other-ways-to-use/1-stream-processor.md) container.

In this example, we will set up a monitor on a live stream of a bird feeder and configure Groundlight to alert us when a bird is present at the feeder.

## Requirements

- [Docker](https://www.docker.com/) installed on your system
- A YouTube live stream URL or video ID you'd like to monitor. For example, this live stream of a Bird Feeder in Panama hosted by the Cornell Lab of Ornithology: [`https://www.youtube.com/watch?v=WtoxxHADnGk`](https://www.youtube.com/watch?v=WtoxxHADnGk)
- A [Groundlight account](https://dashboard.groundlight.ai)



## Installation

Pull the Groundlight Stream container:

```bash
docker pull groundlight/stream
```

## Creating the Monitor

The Groundlight Stream container makes it easy to monitor video streams. Here's how to use it:

1. First, get (or create) your API token from the [Groundlight dashboard](https://dashboard.groundlight.ai/reef/my-account/api-tokens). Set your Groundlight API token as an environment variable:

```bash
export GROUNDLIGHT_API_TOKEN="<your-api-token>"
```

2. Create a Binary-mode detector in the [dashboard](https://dashboard.groundlight.ai). Set the question to "Is there a bird at the feeder?" and the confidence threshold to 0.75. Note the detector ID for later use.

:::tip

We use a relatively low confidence threshold in this example because birdwatching is a fun and casual activity. For more critical applications, you may want to set a higher confidence threshold.

:::

3. Now, run the Groundlight Stream container to process the live stream. For example, to monitor the Cornell Lab of Ornithology's bird feeder live stream, you could use the following command:

```bash
docker run groundlight/stream \
    -t "$GROUNDLIGHT_API_TOKEN" \
    -d "<YOUR_DETECTOR_ID>" \
    -s "https://www.youtube.com/watch?v=WtoxxHADnGk" \
    -f 0.25 \   # 1 frame every 4 seconds
    -m \        # enable motion detection to only process frames when movement occurs
    -v          # enable verbose logging
```
You should see Image Queries being submitted to Groundlight as the container processes the live stream. Once you have confirmed that the container is working as expected, you can remove the `-v` flag to reduce the amount of logging, and you can also run the container in the background by adding the `--detach` flag.
```bash
docker run --detach groundlight/stream \
    -t "$GROUNDLIGHT_API_TOKEN" \
    -d "<YOUR_DETECTOR_ID>" \
    -s "https://www.youtube.com/watch?v=WtoxxHADnGk" \
    -f 0.25 \   # 1 frame every 4 seconds
    -m          # enable motion detection to only process frames when movement occurs
```

4. Finally, let's set up an Alert to notify you when a bird visits the feeder. In the Groundlight dashboard:

   1. Navigate to [the Alerts tab](https://dashboard.groundlight.ai/reef/alerts) and click "Create New Alert"
   2. Enter a descriptive name like for the alert, such as "Bird at feeder"
   3. Select your bird detector by name
   4. Set the alert condition to `Gives answer 'Yes' For 1 Consecutive answer(s)`
   5. Choose "Text" as the Alert Type and enter your phone number
   6. Enable "Include image in message" to receive a photo of the bird with each alert (optional)
   7. Enable a 5-minute snooze period to prevent alert fatigue (optional)
   8. Click "Create" to activate your alert

5. Now, sit back and relax! The container will begin submitting frames from the live stream to Groundlight. You will receive alerts when a bird is detected at the feeder.

## Additional Options

You can also use `groundlight/stream` to process local video files, RTSP streams, and more. Here are some examples:
- Process local video files by mounting them:
```bash
docker run -v /path/to/video:/videos groundlight/stream \
    -t "$GROUNDLIGHT_API_TOKEN" \
    -d <YOUR_DETECTOR_ID> \
    -s /videos/video.mp4
```

- Connect to RTSP cameras:
```bash
docker run groundlight/stream \
    -t "$GROUNDLIGHT_API_TOKEN" \
    -d <YOUR_DETECTOR_ID> \
    -s "rtsp://username:password@camera_ip:554/stream"
```

See the complete documentation at https://github.com/groundlight/stream