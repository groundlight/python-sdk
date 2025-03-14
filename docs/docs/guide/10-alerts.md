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

Groundlight supports the following alerts via Email, Text Message (SMS), and Webhooks.
