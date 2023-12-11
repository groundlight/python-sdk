# Building CV Applications on Raspberry Pi

Raspberry Pi offers a great platform for computer vision (CV), ranging from home hobby projects to serious industrial applications. However, setting up a Raspberry Pi for computer vision can be a time-consuming process. [Groundlight Pi-Gen](https://github.com/groundlight/groundlight-pi-gen), simplifies the setup process by providing ready-to-use OS images for Raspberry Pi.

(Note that here, when we say "image" we mean an OS image, which is a file containing a snapshot of an operating system that can be installed onto a new machine.  These are not photos or pictures, which are also of course important in computer vision.  Oh jargon...)

## Raspberry Pi OS Images pre-built with Computer Vision Software
Go to the [releases](https://github.com/groundlight/groundlight-pi-gen/releases) section in Groundlight Pi-Gen to find Raspberry Pi OS images (`.img.xz` files) that have pre-configured software environments for computer vision. These images are ready to be flashed onto a Raspberry Pi.

These include a fast, modern version of python (3.11), along with key libraries like [OpenCV](https://opencv.org/), [Numpy](https://numpy.org/), [FrameGrab](https://pypi.org/project/framegrab/), and of course [Groundlight](https://pypi.org/project/groundlight/).

There are several flavors of OS image available.  The smaller ones are suitable for headless use, while the larger ones include a desktop GUI with a browser.  The key differences are the size of the download, and the amount of time it takes to flash the image onto a microSD card.  The available flavors are:

- `sdk`: Minimal image with the Python SDK and core libraries.  Suitable for headless use on smaller Raspberry Pi models such as the Pi Zero.
- `mns`: Image with Groundlight Monitoring Notification Server (MNS) for headless use.
- `full`: Image with Groundlight MNS and a desktop GUI with a browser.  Appropriate for a Raspberry Pi with a screen attached.

Note that the `edge` version which will download and run the ML models locally is not yet supported on Raspberry Pi.

## Raspberry Pi Imager and OS Customization
Once you have downloaded your image file, the next step is to flash it onto a microSD card.  To do this, 
download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) software. After selecting your hardware type, pick "Operating System" and then "Use custom" to select the `.img.xz` file you downloaded.
After you select your storage, and hit "Next", you'll encounter the "OS customization" option. Choose "Edit settings" to enter your login credentials, SSH key, and Wi-Fi information.  If this works properly, you'll be able to access your Raspberry Pi over the network without needing to plug in a keyboard, mouse, or monitor.  (We like to plug it into Ethernet for the first boot, because we find that the Raspberry Pi's Wi-Fi can be a bit finicky, even if properly configured.)

### Accessing the Monitoring Notification Server (MNS)
The [Monitoring Notification Server (MNS)](https://github.com/groundlight/monitoring-notification-server) is a web application that allows you set up a computer vision pipeline without writing any code, and have it notify you when it detects something of interest.
After setting up your Raspberry Pi with Groundlight OS, wait a few minutes for it to finish downloading everything, and then access the MNS by navigating to `http://[your-raspberry-pi's-IP-address]:3000` in a web browser.  It will prompt you for your [Groundlight API token](http://localhost:3000/python-sdk/docs/getting-started/api-tokens), which you can get with a free account at [app.groundlight.ai](https://app.groundlight.ai).  Then you can describe your visual query in natural language, and how you want the MNS to notify you when it detects something of interest.

## Get Started
To start building your own computer vision solutions, sign up for a free account at [app.groundlight.ai](https://app.groundlight.ai). Dive into Groundlight Pi-Gen for a hassle-free introduction to AI-powered computer vision on Raspberry Pi.

If you have any questions, please reach out to us on the in-application chat at [app.groundlight.ai](https://app.groundlight.ai) or on [GitHub](https://github.com/groundlight/python-sdk/issues).
