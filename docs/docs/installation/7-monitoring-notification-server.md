# Monitoring Notification Server

This is the easiest way to deploy your Groundlight detectors on a linux computer. All configuration is done through a web user interface, and no code development is required.

## Prerequisites

1. Internet connected linux computer
2. Video source (USB camera or RTSP stream)
3. Groundlight API Key (available from [groundlight.ai](https://www.groundlight.ai/))

## Using the Application

Our Monitoring Notification Server is a server you can deploy anywhere to easily build Groundlight Detectors, and configure them to pull from custom image sources and post notifications.

The Monitoring Notification Server has a simple web interface (depected below) that allows you to configure your detector(s), and a backend that runs on your device to pull images from your camera and post notifications.

### Intro Page

![Intro Page](/img/docker-img-frontpage.png)

### Detector Dashboard

![Detector Dashboard](/img/docker-img-dashboard.png)

## Running the server

There are several ways to deploy the code:

- Using Docker Compose
- Using AWS Greengrass
- Using Kubernetes

### Running with Docker Compose

1. Use the file [`docker-compose.yml`](https://github.com/groundlight/monitoring-notification-server/blob/main/deploy/docker-compose.yml).

2. Run `docker-compose up` in the same directory as the `docker-compose.yml` file.

> If you're using Docker Compose v2, replace `docker-compose` with `docker compose`.

### Running from Docker Compose on 32-bit ARM (armv7)

32-bit arm requires different binary images.

1. Use the slightly different [`docker-compose-armv7.yml`](https://github.com/groundlight/monitoring-notification-server/blob/main/deploy/docker-compose-armv7.yml).

2. Run `docker-compose -f docker-compose-armv7.yml up`.

> If you're using Docker Compose v2, replace `docker-compose` with `docker compose`.

### Running with AWS Greengrass

Before creating the component, run `sudo usermod -aG docker ggc_user` on your Greengrass device to allow the Greengrass service to access the host's Docker daemon.

1. Create a new Greengrass Component
2. Select "Enter recipe as YAML"
3. Paste the YAML from [greengrass-recipe.yaml](https://github.com/groundlight/monitoring-notification-server/blob/main/deploy/greengrass-recipe.yaml) into the text box
4. Click "Create component"
5. Click "Deploy" to deploy the component to your Greengrass group

### Running with Kubernetes

We recommend a minimal Kubernetes install like [k3s](https://k3s.io/).

> Use the file [`kubernetes.yaml`](https://github.com/groundlight/monitoring-notification-server/blob/main/deploy/kubernetes.yaml).

1. Create a Kubernetes cluster and install `kubectl` on your machine.
2. Run `kubectl apply -f kubernetes.yaml` in the same directory as the `kubernetes.yaml` file.

## Building from Source

1. Install [Node.js](https://nodejs.org/en/download/) and [Python 3.8+](https://www.python.org/downloads/).

```bash
git clone https://github.com/groundlight/monitoring-notification-server
cd monitoring-notification-server
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

The FastApi server will be running on [http://0.0.0.0:8000](http://0.0.0.0:8000) – feel free to change the port in `package.json` (you'll also need to update it in `next.config.js`).
