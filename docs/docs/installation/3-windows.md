# Installing on Windows

This guide will help you install the Groundlight SDK on Windows. The Groundlight SDK requires Python 3.8 or higher.

## Prerequisites

Ensure that you have the following installed on your system:

- Python 3.8 or higher
- pip (Python package installer)

## Basic Installation

Assuming you have Python 3.8 or higher installed on your system, you can proceed with the following steps to install or upgrade the Groundlight SDK:

### Installing Groundlight SDK

To install the Groundlight SDK using pip, run the following command in your Command Prompt:

```bash
pip install groundlight
```

If you're also using `python2` on your system, you might need to use `pip3` instead:

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

To check your installed Python version, open a Command Prompt and run:

```bash
python --version
```

If you see a version number starting with "3.9" or higher (e.g., "3.9.7" or "3.12.3"), you're good to go. If not, you might need to upgrade Python on your system.

### Upgrading Python on Windows

Download the latest Python installer from the [official Python website](https://www.python.org/downloads/windows/) and run it.

After upgrading, verify the Python version by running `python --version` or `python3 --version`, as described earlier.

## Ready to go!

You're now ready to start using the Groundlight SDK in your projects. For more information on using the SDK, refer to the [API Tokens](/docs/getting-started/api-tokens) and [Building Applications](/docs/building-applications) documentation pages.

