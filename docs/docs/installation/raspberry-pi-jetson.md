# Installing on Raspberry Pi and NVIDIA Jetson

Groundlight's SDK works great on ARM devices like Raspberry Pi and NVIDIA Jetson.

```
pip3 install groundlight
```

an ARM-compatible version will automatically get installed.  For more detailed instructions refer to the [linux installation instructions](linux-windows-mac.md).

## Using RTSP Streams

If you have `docker` installed on your Pi, you can even just run

```
docker run groundlight/stream
```

as we publish an ARM version of our streaming application to dockerhub.

## Sample application

For a complete end-to-end example of running on a Raspberry pi, see [this github repo](https://github.com/groundlight/raspberry-pi-door-lock).