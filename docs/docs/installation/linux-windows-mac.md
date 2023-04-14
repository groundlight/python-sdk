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


## Checking Python Version

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

### Upgrading Python

If your installed Python version is lower than 3.7, you'll need to upgrade. Follow the instructions for your operating system:

- **Windows**: Download the latest Python installer from the [official Python website](https://www.python.org/downloads/windows/) and run it.

- **macOS**: Download the latest Python installer from the [official Python website](https://www.python.org/downloads/mac-osx/) and run it, or use [Homebrew](https://brew.sh/) to install Python:

  ```bash
  brew install python
  ```

- **Linux**: Use your distribution's package manager to install the latest Python version:

  - For Ubuntu or Debian-based systems:

    ```bash
    sudo apt update
    sudo apt install python3
    ```

  - For Fedora-based systems:

    ```bash
    sudo dnf install python3
    ```

  - For Arch Linux:

    ```bash
    sudo pacman -S python
    ```

After upgrading, verify the Python version by running `python --version` or `python3 --version`, as described earlier.


## Ready to go!

You're now ready to start using the Groundlight SDK in your projects. For more information on using the SDK, refer to the [API Tokens](../getting-started/api-tokens) and [Building Applications](../category/building-applications) documentation pages.

