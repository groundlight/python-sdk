## Instructions for common platforms

### Ubuntu 18.04

Ubuntu 18.04 still uses python 3.6 by default, which is end-of-life. We recommend setting up python 3.8 as follows:

```shell
# Prepare Ubuntu to install things
sudo apt-get update
# Install the basics
sudo apt-get install -y python3.8 python3.8-distutils curl
# Configure `python3` to run python3.8 by default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 10
# Download and install pip3.8
curl https://bootstrap.pypa.io/get-pip.py > /tmp/get-pip.py
sudo python3.8 /tmp/get-pip.py
# Configure `pip3` to run pip3.8
sudo update-alternatives --install /usr/bin/pip3 pip3 $(which pip3.8) 10
# Now we can install Groundlight!
pip3 install groundlight
```
