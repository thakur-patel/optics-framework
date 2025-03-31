# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os
from optics_framework.helper.version import VERSION
project = 'Optics Framework'
copyright = '2025, Lalitanand Dandge'
author = 'Lalitanand Dandge'
release = VERSION

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.graphviz",
              "sphinx.ext.imgconverter",
              "sphinx.ext.autodoc",
              "sphinx.ext.autosummary",
              ]
autosummary_generate = True


templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    'navigation_depth': 2,
    'collapse_navigation': True,
}
html_sidebars = {
    "**": ["sidebar-nav-bs"],
}

sys.path.insert(0, os.path.abspath('../../Optics_Framework'))
