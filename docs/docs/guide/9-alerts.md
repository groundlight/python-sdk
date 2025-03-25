# Configuring Alerts

Groundlight supports triggering alerts based on the results of image queries. Alerts can be configured to notify you when a specific condition is met.

To configure an alert, navigate to [the **Alerts** tab on the Groundlight dashboard](https://dashboard.groundlight.ai/reef/alerts). Here, you can create a new alert by clicking the **Create New Alert** button.

## Alert Configuration

When creating a new alert, you can configure alerts for the following conditions:
1. A specific answer is returned N times in a row.
2. The answer changes from one value to another.
3. There are no changes in the answer for a specified period of time.
4. There are no queries submitted for a specified period of time.

A snooze period can be configured to prevent the alert from triggering multiple times in quick succession.

Optionally, you can configure the alert to include the triggering image in the alert message.

:::tip

Consider configuring a "no queries submitted" alert to monitor system health. If your application is expected to submit queries regularly (e.g., monitoring a camera feed), setting an alert for when no queries are received for a few minutes can help quickly identify if your system has gone offline or is experiencing connectivity issues.

:::

## Alert Mediums

Groundlight supports alerts via Email, Text Message (SMS), and Webhooks.

### Webhooks

By setting up a webhook alert for your Groundlight detector, you can integrate Groundlight's computer vision technology with your existing messaging platform, other tech stack, or even a custom application.

You can either set up an alert using one of our default templates (currently available for Slack, more platforms to come), or build your own.

#### Custom Templates

We use Jinja2 to manage and render templates. See the ([Jinja template documentation](https://jinja.palletsprojects.com/en/stable/templates/)) for information on how to construct your template.
The template will need to be a valid Jinja template which renders to valid JSON to be used as a payload for your webhook alert. 

We provide a set of variables which you can use to put information about your detector and alert into your template. 
The available variables are:

- `detector_name`: The name of your detector that the alert was triggered on
- `detector_query`: The detector's query.
- `detector_id`: The detector's unique ID
- `confidence_threshold`: The current confidence threshold for the detector.
- `detector_mode`: The detector's mode (binary, count, multiclass, etc). Currently, alerts are only available for binary detectors.
- `image_query_id`: The id of the image query which triggered the alert
- `time_repr`: A human readable string of the time the alert was triggered in UTC. Does not include the date.
- `activation_time`: The time and date the alert was triggered in UTC.
- `condition_repr`: The condition the alert is configured with, put into a human-readable string (eg. " returned a YES answer at ").
- `image_url`: An image URL to access the image which triggered the alert. Only available if the alert was configured with `include_image` set to True.

For example, the template below could be used as a custom payload to configure a Slack alert which includes a basic message and the triggering image.
```
"""{
    "text": "Alert activated on Groundlight detector {{ detector_name }} (Query: {{ detector_query }}). Detector {{ condition_repr }} {{ time_repr }}",
    "attachments": [
        {
            "fallback": "Optional image attachment for the detector alert.",
            "image_url": "{{ image_url }}",
            "title": "Related Image"
        }
    ]
}"""
```

#### Headers

Optionally, you can also configure the headers for your webhook alert POST request. This is particularly useful if your application requires a specific security token to be present to accept incoming POST requests. 
If your application requires headers, you can provide them as a JSON dictionary. If not, you can configure your template and leave the headers blank.