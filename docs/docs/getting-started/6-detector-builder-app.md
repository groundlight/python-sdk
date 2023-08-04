# Detector Builder App

This is the easiest way to deploy your Groundlight detector on your computer, Raspberry Pi, or any other device that supports Docker. This method does not require any coding, and configuration is done through a web interface.

## Prerequisites

1. You must have a linux machine that can run Docker
2. The machine must have internet access
3. You must have an API key for the Groundlight API
4. Either a usb camera/raspberry pi camera must be plugged into your machine, or there must be an rtsp stream available at the url you provide
5. The machine must be able to host a local web server

## Deployment

1. Install Docker on your computer. See [Docker's installation instructions](https://docs.docker.com/get-docker/).
2. Create a new file called `docker-compose.yml` in your project directory. Copy the following into it:

```yaml
services:
  frontend:
    image: docker.io/maxatgroundlight/detector-builder-frontend:latest
    ports:
      - "3000:3000"
    depends_on:
      - backend
  backend:
    image: docker.io/maxatgroundlight/detector-builder-backend:latest
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

![Screenshot of the Groundlight Edge Client](/img/docker-img-frontpage.png)
