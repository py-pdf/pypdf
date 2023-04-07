"""Test the pypdf.constants module."""
import re
from typing import Callable

from pypdf.constants import PDF_KEYS


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
            if attr.startswith("__") and attr.endswith("__"):
                continue
            constant_value = getattr(cls, attr)
            if isinstance(constant_value, Callable):
                continue
            assert constant_value.startswith("/")
            assert pattern.match(constant_value)
            assert attr.replace("_", "").lower() == constant_value[1:].lower()
