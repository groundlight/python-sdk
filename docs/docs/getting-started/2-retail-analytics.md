# A Serious Example: Retail Analytics

## Tracking utilization of a customer service counter

This example demonstrates the application of Groundlight to a retail analytics solution, which monitors the usage of a service counter by customers throughout the day. The application creates a detector to identify when the service desk is being utilized by a customer. It checks the detector every minute, and once an hour, it prints out a summary of the percentage of time that the register is in use. At the end of the day, it emails the daily log.

This retail analytics application can be beneficial in various ways:

1. **Staff allocation and scheduling:** By analyzing the usage patterns of the service counter, store managers can optimize staff allocation and scheduling, ensuring that enough employees are available during peak hours and reducing wait times for customers.

1. **Identifying trends:** The application can help identify trends in customer behavior, such as busier times of the day or specific days of the week with higher traffic. This information can be used to plan targeted marketing campaigns or promotions to increase sales and customer engagement.

1. **Improving store layout:** Understanding when and how often customers use the service counter can provide insights into the effectiveness of the store's layout. Retailers can use this information to make data-driven decisions about rearranging the store layout to encourage customers to visit the service counter or explore other areas of the store.

1. **Customer satisfaction:** By monitoring the usage of the service counter and proactively addressing long wait times or crowded areas, retailers can improve customer satisfaction and loyalty. A positive customer experience can lead to increased sales and return visits.

To implement this retail analytics solution, a store would need to install a supported camera near the service counter, ensuring a clear view of the area. The camera would then be connected to a computer running the Groundlight-based application. Store managers would receive hourly summaries of the service counter usage and a daily log via email, enabling them to make informed decisions to improve store operations and customer experience.

## Requirements

- [Groundlight SDK](/docs/installation/) with Python 3.7 or higher
- A supported USB or network-connected camera
- An email account with SMTP access to send the daily log

## Installation

Ensure you have Python 3.7 or higher installed, and then install the Groundlight SDK, OpenCV library, and other required libraries:

```bash
pip install groundlight opencv-python pillow
```

## Creating the Application

1. First, log in to the [Groundlight application](https://app.groundlight.ai) and get an [API Token](api-tokens).

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

4. Define a function to send the daily log via email:

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

5. Write the main application loop:

```python notest
gl = Groundlight()

detector = gl.get_detector("Customer At Register Detector")

log = []
hourly_start = datetime.now()
daily_start = datetime.now()

while True:
    image = capture_image()
    if image:
        try:
            iq = gl.submit_image_query(image=image, detector=detector, wait=60)
            result = iq.result
            log.append(result)
            if datetime.now() - hourly_start >= timedelta(hours=1):
                hourly_start = datetime.now()
                percent_in_use = (log.count("YES") / len(log)) * 100
                print(f"Hourly summary: {percent_in_use:.2f}% register in use")

            if datetime.now() - daily_start >= timedelta(days=1):
                daily_start = datetime.now()
                daily_percent_in_use = (log.count("YES") / len(log)) * 100
                daily_log = f"Daily summary: {daily_percent_in_use:.2f}% register in use"
                print(daily_log)
                send_email("you@example.com", "receiver@example.com", "Daily Register Usage Log", daily_log)
                log = []
        except Exception as e:
            print(f"Error submitting image query: {e}")
    else:
        print("Failed to capture image")

    # Sleep for a minute before checking again
    time.sleep(60)
```

This application captures an image using the `capture_image` function, then submits it to the Groundlight API for analysis. If a customer is detected at the register, it logs the event. Every hour, it prints a summary of the register's usage percentage, and at the end of the day, it emails the daily log using the `send_email` function.

Save the script as `customer_at_register_detector.py` and run it:

```bash
python customer_at_register_detector.py
```

