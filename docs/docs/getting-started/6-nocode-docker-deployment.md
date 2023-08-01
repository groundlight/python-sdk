# No-Code Deployment with Docker

This is the easiest way to deploy your Groundlight detector on your computer, Raspberry Pi, or any other device that supports Docker. This method does not require any coding, and configuration is done through a web interface.

1. Install Docker on your computer. See [Docker's installation instructions](https://docs.docker.com/get-docker/).
2. Create a new file called `docker-compose.yml` in your project directory. Copy the following into it:

```yaml
services:
  frontend:
    image: docker.io/maxatgroundlight/groundlight-edge-client-frontend:latest
    ports:
      - "3000:3000"
    depends_on:
      - backend
  backend:
    image: docker.io/maxatgroundlight/groundlight-edge-client-backend:latest
    ports:
      - "8000:8000"
```

3. Run the following command in your project directory:

```bash
docker-compose up
```

4. If installed locally, open http://localhost:3000 in your browser. If installed on a remote device, replace `localhost` with the IP address of your device. You should see the following page:

![Screenshot of the Groundlight Edge Client](/img/docker-img-frontpage.png)
