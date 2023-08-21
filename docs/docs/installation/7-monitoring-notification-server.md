# Monitoring Notification Server

This is the easiest way to deploy your Groundlight detectors on a linux computer. All configuration is done through a web user interface, and no code development is required.

## Prerequisites

1. Internet connected linux computer
2. Video source (USB camera or RTSP stream)
3. Groundlight API Key

## Deployment

1. Install Docker on your computer. See [Docker's installation instructions](https://docs.docker.com/get-docker/).
2. Create a new file called `docker-compose.yml` in your project directory. Copy the following into it:

```yaml
services:
  frontend:
    image: docker.io/groundlight/monitoring-notification-server-frontend:latest
    ports:
      - "3000:3000"
    depends_on:
      - backend
  backend:
    image: docker.io/groundlight/monitoring-notification-server-backend:latest
    ports:
      - "8000:8000"
    devices:
      - /dev/video0:/dev/video0
      - /dev/video1:/dev/video1
      - /dev/video2:/dev/video2
      - /dev/video3:/dev/video3
    privileged: true
    volumes:
      - /dev/bus/usb:/dev/bus/usb
```

3. Run the following command in your project directory:

```bash
docker-compose up
```

4. If installed locally, open http://localhost:3000 in your browser. If installed on a remote device, replace `localhost` with the IP address of your device. You should see the following page:

![Screenshot of the Groundlight Monitoring Notification Server](/img/docker-img-frontpage.png)
