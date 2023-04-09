"""Test the pypdf.constants module."""
import re
from typing import Callable

from pypdf.constants import PDF_KEYS, GraphicsStateParameters


def test_slash_prefix():
    """
    Naming conventions of PDF_KEYS (constant names) are followed.

    This test function validates if PDF key names follow the required pattern:
    - Starts with a slash '/'
    - Followed by an uppercase letter
    - Contains alphanumeric characters (letters and digits)
    - The attribute name should be a case-insensitive match, with underscores removed
    """
    pattern = re.compile(r"^\/[A-Z]+[a-zA-Z0-9]*$")
    for cls in PDF_KEYS:
        for attr in dir(cls):
            # Skip magic methods
            if attr.startswith("__") and attr.endswith("__"):
                continue

            # Skip methods
            constant_value = getattr(cls, attr)
            if isinstance(constant_value, Callable):
                continue

            assert constant_value.startswith("/")
            assert attr.replace("_", "").lower() == constant_value[1:].lower()

            # There are a few exceptions that may be lowercase
            if cls == GraphicsStateParameters and attr in ["ca", "op"]:
                continue
            assert pattern.match(constant_value)
