# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Add the src directory to sys.path so Sphinx can find your package
import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Bicep lint SARIF fixer"
copyright = "2024-%Y, Balazs Hamorszky"
author = "Balazs Hamorszky"
release = "0.0.0a"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.insert(0, os.path.abspath("../src"))  # Adjust relative path if needed

# General configuration
extensions = [
    "sphinx.ext.autodoc",  # For generating documentation from docstrings
    "sphinx.ext.napoleon",  # For parsing Google and NumPy style docstrings
    "sphinx.ext.viewcode",  # To include links to source code
    "sphinxarg.ext",
]

templates_path = ["_templates"]  # Path for custom templates
exclude_patterns = []  # Files to exclude

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "exclude-members": "main",
    "member-order": "bysource",
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_context = {"default_mode": "auto"}
