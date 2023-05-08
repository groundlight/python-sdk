# Installing on Raspberry Pi

This guide will help you install the Groundlight SDK on Raspberry Pi. The Groundlight SDK requires Python 3.7 or higher.

## Prerequisites

Ensure that you have the following installed on your Raspberry Pi:

- Python 3.7 or higher
- pip (Python package installer)

## Basic Installation

Assuming you have Python 3.7 or higher installed on your Raspberry Pi, you can proceed with the following steps to install or upgrade the Groundlight SDK:

### Installing Groundlight SDK

To install the Groundlight SDK using pip, run the following command in your terminal:

```bash
pip3 install groundlight
```

An ARM-compatible version will automatically get installed. The Groundlight SDK is now installed and ready for use.

## Using RTSP Streams

If you have `docker` installed on your Raspberry Pi, you can even just run

```bash
docker run groundlight/stream
```

as we publish an ARM version of our streaming application to Docker Hub.

## Sample application

For a complete end-to-end example of running on a Raspberry Pi, see [this GitHub repo](https://github.com/groundlight/raspberry-pi-door-lock).

## Ready to go!

You're now ready to start using the Groundlight SDK in your projects. For more information on using the SDK, refer to the [API Tokens](/docs/getting-started/api-tokens) and [Building Applications](/docs/building-applications) documentation pages.


