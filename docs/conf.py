"""Sphinx configuration."""

project = "Intellifire4Py"
author = "Jeff Stein"
copyright = "2021, Jeff Stein"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
    "sphinx_copybutton",
]
autoclass_content = "both"
autodoc_typehints = "description"
html_theme = "furo"
