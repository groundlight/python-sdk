# Installing on Linux

This guide will help you install the Groundlight SDK on Linux. The Groundlight SDK requires Python 3.10 or higher.

## Prerequisites

Ensure that you have the following installed on your system:

- Python 3.10 or higher
- pip (Python package installer)

## Basic Installation

Assuming you have Python 3.10 or higher installed on your system, you can proceed with the following steps to install or upgrade the Groundlight SDK:

### Installing Groundlight SDK

To install the Groundlight SDK using pip, run the following command in your terminal:

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

or the groundlight command line tool that comes with the SDK:

```bash
groundlight --help
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

To check your installed Python version, open a terminal and run:

```bash
python --version
```

If you see a version number of "3.10" or higher (e.g., "3.10.12" or "3.12.0"), you're good to go. If not, you might need to upgrade Python on your system.

### Upgrading Python on Linux

Use your distribution's package manager to install the latest Python version:

- For Ubuntu or Debian-based systems:

  ```bash
  sudo apt update
  sudo apt install python3
  ```

  (For Ubuntu releases before 22.04 see note below.)

- For Fedora-based systems:

  ```bash
  sudo dnf install python3
  ```

- For Arch Linux:

  ```bash
  sudo pacman -S python
  ```

After upgrading, verify the Python version by running `python --version` or `python3 --version`, as described earlier.

### Special note about older Ubuntu releases

Ubuntu releases before 22.04 ship a Python version older than 3.10 (for example, 20.04 ships 3.8), and their standard package repositories don't include 3.10 or newer. If you can, upgrade to Ubuntu 22.04 or later. Otherwise, install a newer Python alongside the system one using a tool like [uv](https://docs.astral.sh/uv/) or [pyenv](https://github.com/pyenv/pyenv). Don't replace the system `python3`, since the operating system depends on it. For example, with uv:

```shell
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Create a virtual environment with Python 3.12 (uv downloads it if needed)
uv venv --python 3.12
source .venv/bin/activate
# Now we can install Groundlight!
uv pip install groundlight
```

## Ready to go!

You're now ready to start using the Groundlight SDK in your projects. For more information on using the SDK, refer to the [API Tokens](../getting-started/5-api-tokens.md) documentation and the [Building Applications Guide](../guide/).
