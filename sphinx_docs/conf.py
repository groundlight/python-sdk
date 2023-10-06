# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


import sys
import os

sys.path.insert(0, os.path.abspath("../src"))

project = "Groundlight Python SDK"
copyright = "2023, Groundlight AI <support@groundlight.ai>"
author = "Groundlight AI <support@groundlight.ai>"
release = "0.11.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# sphinx.ext.autodoc is a Sphinx extension that automatically documents Python modules.
# sphinx.ext.napoleon is a Sphinx extension that enables Sphinx to understand Google style docstrings.
# We are using the `reStructuredText` format for docstrings instead of google style, but functions that
# use google style docstrings will still be documented correctly.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
