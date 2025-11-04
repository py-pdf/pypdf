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
from pathlib import Path

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
    "sphinx.ext.doctest",
    # External
    "myst_parser",
]

python_version = ".".join(map(str, sys.version_info[:2]))
intersphinx_mapping = {
    "python": (f"https://docs.python.org/{python_version}", None),
    "Pillow": ("https://pillow.readthedocs.io/en/latest/", None),
}

nitpick_ignore_regex = [
    # For reasons unclear at this stage, the io module prefixes everything with _io
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
napoleon_use_rtype = False  # False, so the return type is inline with the description.

# -- Options for Doctest  ------------------------------------------------------

# Most of doc examples use hardcoded input and output file names.
# To execute these examples real files need to be read and written.
#
# By default, documentation examples run with the working directory set to where
# "sphinx-build" command was invoked. To avoid relative paths in docs and to
# allow to run "sphinx-build" command from any directory, we modify the current
# working directory in each tested file. Tests are executed against our
# temporary directory where we have copied all nessesary resources.

pypdf_test_src_root_dir = os.path.abspath(".")
pypdf_test_dst_root_dir = os.path.abspath("_build/doctest/pypdf_test")
if Path(pypdf_test_dst_root_dir).exists():
   shutil.rmtree(pypdf_test_dst_root_dir)
Path(pypdf_test_dst_root_dir).mkdir(parents=True)

doctest_global_setup = f"""
def pypdf_test_global_setup():
    import os
    import shutil
    from pathlib import Path

    src_root_dir = {pypdf_test_src_root_dir.__repr__()}
    dst_root_dir = {pypdf_test_dst_root_dir.__repr__()}

    global pypdf_test_setup
    def pypdf_test_setup(group: str, resources: dict[str, str] = {{}}):
        dst_dir = os.path.join(dst_root_dir, group)
        Path(dst_dir).mkdir(parents=True)
        os.chdir(dst_dir)

        for (src_path, dst_path) in resources.items():
            src = os.path.normpath(os.path.join(src_root_dir, src_path))
            dst = os.path.join(dst_dir, dst_path or os.path.basename(src_path))

            shutil.copyfile(src, dst)

    global pypdf_test_orig_dir
    pypdf_test_orig_dir = os.getcwd()
    os.chdir(dst_root_dir)

pypdf_test_global_setup()
"""

doctest_global_cleanup = f"""
def pypdf_test_global_cleanup():
    import os

    dst_root_dir = {pypdf_test_dst_root_dir.__repr__()}

    has_files = False
    for file_name in os.listdir(dst_root_dir):
        file = os.path.join(dst_root_dir, file_name)
        if os.path.isfile(file):
            if not has_files:
                print("Docs page was not configured propery for running code examples")
                print("Please use 'pypdf_test_setup' function in 'testsetup' directive")
                print("Deleting unexpected file(s) in " + dst_root_dir)
                has_files = True
            print(f"- {{file_name}}")
            os.remove(file)

    os.chdir(pypdf_test_orig_dir)

pypdf_test_global_cleanup()
"""
