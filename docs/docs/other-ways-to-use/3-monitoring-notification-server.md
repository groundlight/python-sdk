# Low-Code Monitoring Notification Server

Groundlight's Monitoring Notification Server (MNS) is the easiest way to deploy your Groundlight detectors on a linux computer. All configuration is done through a web user interface, and no code development is required.

## Prerequisites

1. Internet-connected Linux computer
2. Video source (USB camera or RTSP stream)
3. Groundlight API Key (available from [groundlight.ai](https://www.groundlight.ai/))

## Using the Application

The Monitoring Notification Server is a versatile tool that can be deployed on any server to facilitate the creation and management of Groundlight Detectors. It allows you to configure detectors to retrieve images from custom sources and send notifications.

Featuring an intuitive web interface, the Monitoring Notification Server enables easy configuration of detectors. The server operates on your device, capturing images from your camera and sending notifications as needed.

### MNS Home Page

![Intro Page](/img/docker-img-frontpage.png)

### Detector Dashboard

![Detector Dashboard](/img/docker-img-dashboard.png)

## Running the server

To begin, clone the GitHub repository: https://github.com/groundlight/monitoring-notification-server

```bash
git clone https://github.com/groundlight/monitoring-notification-server.git
cd monitoring-notification-server
```

Deployment options include Docker Compose, AWS Greengrass, and Kubernetes.

### Running with Docker Compose

1. Locate the [`docker-compose.yml`](https://github.com/groundlight/monitoring-notification-server/blob/main/deploy/docker-compose.yml) file.

2. Run `docker-compose up` in the directory containing the `docker-compose.yml` file (the root of the repository).

:::tip
If you're using Docker Compose v2, replace `docker-compose` with `docker compose`.
:::

### Running from Docker Compose on 32-bit ARM (armv7)

32-bit arm requires different binary images.

1. Use the slightly different [`docker-compose-armv7.yml`](https://github.com/groundlight/monitoring-notification-server/blob/main/deploy/docker-compose-armv7.yml).

2. Run `docker-compose -f docker-compose-armv7.yml up`.

### Running with AWS Greengrass

Before creating the component, run `sudo usermod -aG docker ggc_user` on your Greengrass device to allow the Greengrass service to access the host's Docker daemon.

1. Create a new Greengrass Component
2. Select "Enter recipe as YAML"
3. Paste the YAML from [greengrass-recipe.yaml](https://github.com/groundlight/monitoring-notification-server/blob/main/deploy/greengrass-recipe.yaml) into the text box
4. Click "Create component"
5. Click "Deploy" to deploy the component to your Greengrass group

### Running with Kubernetes

For a minimal Kubernetes setup, we recommend using [k3s](https://k3s.io/).

1. Set up a Kubernetes cluster and install `kubectl` on your machine.
2. Apply the Kubernetes configuration by running:
   ```bash
   kubectl apply -f kubernetes.yaml
   ```
   Ensure you are in the directory containing the [`kubernetes.yaml`](https://github.com/groundlight/monitoring-notification-server/blob/main/deploy/kubernetes.yaml) file.

## Building from Source

1. Install [Node.js](https://nodejs.org/en/download/) and [Python 3.9+](https://www.python.org/downloads/).

```bash
git clone https://github.com/groundlight/monitoring-notification-server
cd monitoring-notification-server
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

The FastApi server will be running on [http://0.0.0.0:8000](http://0.0.0.0:8000) – feel free to change the port in `package.json` (you'll also need to update it in `next.config.js`).
