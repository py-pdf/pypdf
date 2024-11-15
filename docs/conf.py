"""
Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options.
For a full list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import datetime
import os
import shutil
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../"))

import pypdf as py_pkg

shutil.copyfile("../CHANGELOG.md", "meta/CHANGELOG.md")
shutil.copyfile("../CONTRIBUTORS.md", "meta/CONTRIBUTORS.md")

# -- Project information -----------------------------------------------------

project = py_pkg.__name__
copyright = f"2006 - {datetime.datetime.now(tz=datetime.timezone.utc).year}, Mathieu Fenniak and pypdf contributors"
author = "Mathieu Fenniak"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = py_pkg.__version__
# The full version, including alpha/beta/rc tags.
release = py_pkg.__version__

# -- General configuration ---------------------------------------------------
# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = "4.0.0"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    # External
    "myst_parser",
]

python_version = ".".join(map(str, sys.version_info[:2]))
intersphinx_mapping = {
    "python": (f"https://docs.python.org/{python_version}", None),
    "Pillow": ("https://pillow.readthedocs.io/en/latest/", None),
}

nitpick_ignore_regex = [
    # For reasons unclear at this stage the io module prefixes everything with _io
    # and this confuses sphinx
    (
        r"py:class",
        r"(_io.(FileIO|BytesIO|Buffered(Reader|Writer))|pypdf.*PdfDocCommon)",
    ),
]

autodoc_default_options = {
    "member-order": "bysource",
    "members": True,
    "show-inheritance": True,
    "undoc-members": True,
}
autodoc_inherit_docstrings = False
autodoc_typehints_format = "short"
python_use_unqualified_type_names = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Configure MyST extension.
myst_all_links_external = False
myst_heading_anchors = 3


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages. See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further. For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "canonical_url": "",
    "analytics_id": "",
    "logo_only": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}
html_logo = "_static/logo.png"


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Options for Napoleon  -----------------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = False  # Explicitly prefer Google style docstring
napoleon_use_param = True  # for type hint support
napoleon_use_rtype = False  # False so the return type is inline with the description.
