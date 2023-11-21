---
sidebar_position: 6
---

# Using Groundlight on the Edge

If your account has access to edge models, you can download and install them to your edge devices.  
This allows you to run your model evaluations on the edge, reducing latency, cost, network bandwidth, and energy.

## How the Edge Endpoint works

The Edge Endpoint runs as a set of docker containers on an "edge device".  This edge device can be an NVIDIA Jetson device, rack-mounted server, or even a Raspberry Pi.  The Edge Endpoint is responsible for downloading and running the models, 
and for communicating with the Groundlight cloud service.

To use the edge endpoint, simply configure the Groundlight SDK to use the edge endpoint's URL instead of the cloud endpoint.
All application logic will work seamlessly and unchanged with the Groundlight Edge Endpoint, except some ML answers will
return much faster locally.  The only visible difference is that image queries answered at the edge endpoint will have the prefix `iqe_` instead of `iq_` for image queries answered in the cloud.  `iqe_` stands for "image query edge".  Edge-originated
image queries will not appear in the cloud dashboard.

## Configuring the Edge Endpoint

To configure the Groundlight SDK to use the edge endpoint, you can either pass the endpoint URL to the Groundlight constructor like:

```python
from groundlight import Groundlight
gl = Groundlight(endpoint="http://localhost:6717")
```

or by setting the `GROUNDLIGHT_ENDPOINT` environment variable like:

```bash
export GROUNDLIGHT_ENDPOINT=http://localhost:6717
python your_app.py
```