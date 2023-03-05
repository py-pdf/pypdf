"""
Testing the text-extraction submodule and ensuring the quality of text extraction.

The tested code might be in _page.py.
"""

from pathlib import Path

from pypdf import PdfReader
from pypdf._text_extraction import set_custom_rtl

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
SAMPLE_ROOT = PROJECT_ROOT / "sample-files"


def test_multi_language():
    reader = PdfReader(RESOURCE_ROOT / "multilang.pdf")
    txt = reader.pages[0].extract_text()
    assert "Hello World" in txt, "English not correctly extracted"
    # iss #1296
    assert "مرحبا بالعالم" in txt, "Arabic not correctly extracted"
    assert "Привет, мир" in txt, "Russian not correctly extracted"
    assert "你好世界" in txt, "Chinese not correctly extracted"
    assert "สวัสดีชาวโลก" in txt, "Thai not correctly extracted"
    assert "こんにちは世界" in txt, "Japanese not correctly extracted"
    # check customizations
    set_custom_rtl(None, None, "Russian:")
    assert (
        ":naissuR" in reader.pages[0].extract_text()
    ), "(1) CUSTOM_RTL_SPECIAL_CHARS failed"
    set_custom_rtl(None, None, [ord(x) for x in "Russian:"])
    assert (
        ":naissuR" in reader.pages[0].extract_text()
    ), "(2) CUSTOM_RTL_SPECIAL_CHARS failed"
    set_custom_rtl(0, 255, None)
    assert ":hsilgnE" in reader.pages[0].extract_text(), "CUSTOM_RTL_MIN/MAX failed"
    set_custom_rtl("A", "z", [])
    assert ":hsilgnE" in reader.pages[0].extract_text(), "CUSTOM_RTL_MIN/MAX failed"
    set_custom_rtl(-1, -1, [])  # to prevent further errors
