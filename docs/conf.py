"""Sphinx configuration for closurelab."""

from importlib.metadata import version as _version

# -- Project information -----------------------------------------------------

project = "closurelab"
author = "Aldo Gargiulo"
copyright = "2026, Aldo Gargiulo"
release = _version("closurelab")

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",  # pull documentation from docstrings
    "sphinx.ext.intersphinx",  # link to external documentation
    "sphinx.ext.viewcode",  # add links to the source code
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Autodoc -----------------------------------------------------------------

autodoc_typehints = "description"

# -- Intersphinx -------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "xarray": ("https://docs.xarray.dev/en/stable/", None),
}

# -- HTML output -------------------------------------------------------------

html_theme = "furo"
