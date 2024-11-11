# A Serious Example: Retail Analytics

## Tracking utilization of a customer service counter

This example demonstrates the application of Groundlight to a retail analytics solution, which monitors the usage of a service counter by customers throughout the day. The application creates a detector to identify when the service desk is being utilized by a customer. It checks the detector every minute, and once an hour, it prints out a summary of the percentage of time that the service counter is in use. At the end of the day, it emails the daily log.

This retail analytics application can be beneficial in various ways:

1. **Staff allocation and scheduling:** By analyzing the usage patterns of the service counter, store managers can optimize staff allocation and scheduling, ensuring that enough employees are available during peak hours and reducing wait times for customers.

1. **Identifying trends:** The application can help identify trends in customer behavior, such as busier times of the day or specific days of the week with higher traffic. This information can be used to plan targeted marketing campaigns or promotions to increase sales and customer engagement.

1. **Improving store layout:** Understanding when and how often customers use the service counter can provide insights into the effectiveness of the store's layout. Retailers can use this information to make data-driven decisions about rearranging the store layout to encourage customers to visit the service counter or explore other areas of the store.

1. **Customer satisfaction:** By monitoring the usage of the service counter and proactively addressing long wait times or crowded areas, retailers can improve customer satisfaction and loyalty. A positive customer experience can lead to increased sales and return visits.

To implement this retail analytics solution, a store would need to install a supported camera near the service counter, ensuring a clear view of the area. The camera would then be connected to a computer running the Groundlight-based application. Store managers would receive hourly summaries of the service counter usage and a daily log via email, enabling them to make informed decisions to improve store operations and customer experience.

## Requirements

- [Groundlight SDK](/docs/installation/) with Python 3.8 or higher
- A supported USB or network-connected camera
- An email account with SMTP access to send the daily log

## Installation

Ensure you have Python 3.8 or higher installed, and then install the Groundlight SDK, OpenCV library, and other required libraries:

```bash
pip install groundlight opencv-python pillow
```

## Creating the Application

1. First, log in to the [Groundlight dashboard](https://dashboard.groundlight.ai) and create an [API Token](https://dashboard.groundlight.ai/reef/my-account/api-tokens).

2. Next, we'll write the Python script for the application. Import the required libraries:

```python notest
import time
import cv2
import smtplib
from groundlight import Groundlight
from PIL import Image
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
```

3. Define a function to capture an image from the camera using OpenCV:

```python
def capture_image():
    cap = cv2.VideoCapture(0)

    ret, frame = cap.read()
    cap.release()

    if ret:
        # Convert to PIL image
        return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    else:
        return None
```

4. Define a function to send the daily log via email.  You will need to customize this for your particular network environment.

```python
def send_email(sender, receiver, subject, body):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.example.com', 587)
    server.starttls()
    server.login(sender, "your-password")
    text = msg.as_string()
    server.sendmail(sender, receiver, text)
    server.quit()
```

5.  Define when your business's operating hours are:

```python notest
START_OF_BUSINESS = 9  # e.g. 9am
END_OF_BUSINESS = 17  # e.g. 5pm

def is_within_business_hours():
    current_hour = datetime.now().hour
    return START_OF_BUSINESS <= current_hour < END_OF_BUSINESS

```


6.  Write the main application loop:

```python notest
gl = Groundlight()

detector = gl.get_or_create_detector(
                name="counter-in-use",
                query="Is there a customer at the service counter?",
                # We can get away with relatively low confidence since we're aggregating
                confidence_threshold=0.8)

DELAY = 60

log = []
daily_log = []
next_hourly_start = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

while True:
    if not is_within_business_hours():
        time.sleep(DELAY)
        continue

    image = capture_image()
    if not image:
        print("Failed to capture image")
        time.sleep(DELAY)
        continue

    try:
        iq = gl.submit_image_query(image=image, detector=detector, wait=60)
    except Exception as e:
        print(f"Error submitting image query: {e}")
        time.sleep(DELAY)
        continue

    answer = iq.result.label
    log.append(answer)

    if datetime.now() >= next_hourly_start:
        next_hourly_start += timedelta(hours=1)

        percent_in_use = (log.count("YES") / len(log)) * 100
        current_time = datetime.now().replace(hour=START_OF_BUSINESS, minute=0, second=0)
        formatted_time = current_time.strftime("%I%p")  # like 3pm
        msg = f"Hourly summary for {formatted_time}: {percent_in_use:.0f}% counter in use"
        print(msg)
        daily_log.append(msg)
        log = []

    current_hour = datetime.now().hour
    if current_hour == END_OF_BUSINESS and not daily_log == []:
        daily_summary = "Daily summary:\n"
        for msg in daily_log:
            daily_summary += f"{msg}\n"

        print(daily_summary)
        send_email(sender="counterbot@example.com",
           receiver="manager@example.com",
           subject="Daily Service Counter Usage Log",
           body=daily_summary)
        daily_log = []

    time.sleep(DELAY)
```

This application captures an image using the `capture_image` function, then submits it to the Groundlight API for analysis. If a customer is detected at the counter, it logs the event. Every hour, it prints a summary of the counter's usage percentage, and at the end of the day, it emails the daily log using the `send_email` function.

Save the script as `service_counter_monitor.py` and run it:

```bash
python service_counter_monitor.py
```
