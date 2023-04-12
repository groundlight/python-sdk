# Ubuntu 18.04

Ubuntu 18.04 still uses python 3.6 by default, which is end-of-life. We generally recommend using python 3.10.  If you know how to install py3.10, please go ahead.  But the easiest version of python 3 to use with Ubuntu 18.04 is python 3.8, which can be installed as follows:

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
