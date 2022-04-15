from PyPDF2.constants import PDF_KEYS


def test_slash_prefix():
    for cls in PDF_KEYS:
        for attr in dir(cls):
            if attr.startswith("__") and attr.endswith("__"):
                continue
            assert getattr(cls, attr).startswith("/")
