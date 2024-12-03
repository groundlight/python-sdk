# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


import os
import sys
from datetime import datetime

import toml

sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(1, os.path.abspath("../generated"))


def get_version_name() -> str:
    pyproject_path = "../pyproject.toml"
    with open(pyproject_path, "r") as f:
        pyproject_deps = toml.load(f)

    version = pyproject_deps["tool"]["poetry"]["version"]
    return version


project = "Groundlight Python SDK"
copyright = f"{datetime.now().year}, Groundlight AI <support@groundlight.ai>"
author = "Groundlight AI <support@groundlight.ai>"
version = get_version_name()
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# sphinx.ext.autodoc is a Sphinx extension that automatically documents Python modules.
# We are using the `reStructuredText` format for docstrings instead of google style.
extensions = ["sphinx.ext.autodoc", "sphinxcontrib.autodoc_pydantic"]

templates_path = ["_templates"]
exclude_patterns = []

# Automatically add type annotations to the generated function signatures and descriptions. This
# means we don't have to manually add :type: annotations into the docstrings.
autodoc_typehints = "both"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
