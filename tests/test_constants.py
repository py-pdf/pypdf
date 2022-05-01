import re

from PyPDF2.constants import PDF_KEYS


def test_slash_prefix():
    pattern = re.compile(r"^\/[A-Z]+[a-zA-Z0-9]*$")
    for cls in PDF_KEYS:
        for attr in dir(cls):
            if attr.startswith("__") and attr.endswith("__"):
                continue
            constant_value = getattr(cls, attr)
            assert constant_value.startswith("/")
            assert pattern.match(constant_value)
            assert attr.replace("_", "").lower() == constant_value[1:].lower()
