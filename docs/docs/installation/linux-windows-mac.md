# Installing on Windows, Linux, or MacOS

This guide will help you install the Groundlight SDK on Windows, Linux, or macOS.  The Groundlight SDK requires Python 3.7 or higher.

## Prerequisites

Ensure that you have the following installed on your system:

- Python 3.7 or higher
- pip (Python package installer)

## Basic Installation

Assuming you have Python 3.7 or higher installed on your system, you can proceed with the following steps to install or upgrade the Groundlight SDK:

### Installing Groundlight SDK

To install the Groundlight SDK using pip, run the following command in your terminal (or Command Prompt on Windows):

```bash
pip install groundlight
```

If you're using `python3`, you might need to use `pip3` instead:

```bash
pip3 install groundlight
```

The Groundlight SDK is now installed and ready for use.

### Checking Groundlight SDK Version

To check if the Groundlight SDK is installed and to display its version, you can use the following Python one-liner:

```bash
python -c "import groundlight; print(groundlight.__version__)"
```

### Upgrading Groundlight SDK

If you need to upgrade the Groundlight SDK to the latest version, use the following pip command:

```bash
pip install --upgrade groundlight
```

Or, if you're using `pip3`:

```bash
pip3 install --upgrade groundlight
```

After upgrading, you can use the Python one-liner mentioned in the "Checking Groundlight SDK Version" section to verify that the latest version is now installed.


## Getting the right Python Version

To check your installed Python version, open a terminal (or Command Prompt on Windows) and run:

```bash
python --version
```

If you see a version number starting with "3.7" or higher (e.g., "3.7.5" or "3.9.0"), you're good to go.

```
pip3 install groundlight --upgrade
```



If the above command does not work or shows a Python 2.x version, try running:

```bash
python3 --version
```

If this command returns a Python 3.7 or higher version, you can use `python3` instead of `python` in the following steps.

### Upgrading Python on Windows

Download the latest Python installer from the [official Python website](https://www.python.org/downloads/windows/) and run it.

### Upgrading Python on MacOS

Download the latest Python installer from the [official Python website](https://www.python.org/downloads/mac-osx/) and run it, or use [Homebrew](https://brew.sh/) to install Python:

  ```bash
  brew install python
  ```

### Upgrading Python on Linux

Use your distribution's package manager to install the latest Python version:

  - For Ubuntu or Debian-based systems:

    ```bash
    sudo apt update
    sudo apt install python3
    ```

    (For Ubuntu 18.04 see note below.)

  - For Fedora-based systems:

    ```bash
    sudo dnf install python3
    ```

  - For Arch Linux:

    ```bash
    sudo pacman -S python
    ```

After upgrading, verify the Python version by running `python --version` or `python3 --version`, as described earlier.

### Special note about Ubuntu 18.04

Ubuntu 18.04 still uses python 3.6 by default, which is end-of-life. We generally recommend using python 3.10. If you know how to install py3.10, please go ahead. But the easiest version of python 3 to use with Ubuntu 18.04 is python 3.8, which can be installed as follows without adding any extra repositories:

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


## Ready to go!

You're now ready to start using the Groundlight SDK in your projects. For more information on using the SDK, refer to the [API Tokens](/docs/getting-started/api-tokens) and [Building Applications](/docs/building-applications) documentation pages.

