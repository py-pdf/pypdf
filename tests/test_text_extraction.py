"""
Testing the text-extraction submodule and ensuring the quality of text extraction.

The tested code might be in _page.py.
"""
from pathlib import Path

import pytest

from pypdf import PdfReader, mult
from pypdf._text_extraction import set_custom_rtl

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
SAMPLE_ROOT = PROJECT_ROOT / "sample-files"


@pytest.mark.parametrize(("visitor_text"), [None, lambda a, b, c, d, e: None])
def test_multi_language(visitor_text):
    reader = PdfReader(RESOURCE_ROOT / "multilang.pdf")
    txt = reader.pages[0].extract_text(visitor_text=visitor_text)
    assert "Hello World" in txt, "English not correctly extracted"
    # iss #1296
    assert "مرحبا بالعالم" in txt, "Arabic not correctly extracted"
    assert "Привет, мир" in txt, "Russian not correctly extracted"
    assert "你好世界" in txt, "Chinese not correctly extracted"
    assert "สวัสดีชาวโลก" in txt, "Thai not correctly extracted"
    assert "こんにちは世界" in txt, "Japanese not correctly extracted"
    # check customizations
    set_custom_rtl(None, None, "Russian:")
    assert ":naissuR" in reader.pages[0].extract_text(
        visitor_text=visitor_text
    ), "(1) CUSTOM_RTL_SPECIAL_CHARS failed"
    set_custom_rtl(None, None, [ord(x) for x in "Russian:"])
    assert ":naissuR" in reader.pages[0].extract_text(
        visitor_text=visitor_text
    ), "(2) CUSTOM_RTL_SPECIAL_CHARS failed"
    set_custom_rtl(0, 255, None)
    assert ":hsilgnE" in reader.pages[0].extract_text(
        visitor_text=visitor_text
    ), "CUSTOM_RTL_MIN/MAX failed"
    set_custom_rtl("A", "z", [])
    assert ":hsilgnE" in reader.pages[0].extract_text(
        visitor_text=visitor_text
    ), "CUSTOM_RTL_MIN/MAX failed"
    set_custom_rtl(-1, -1, [])  # to prevent further errors

    reader = PdfReader(SAMPLE_ROOT / "015-arabic/habibi-rotated.pdf")
    assert "habibi" in reader.pages[0].extract_text(visitor_text=visitor_text)
    assert "حَبيبي" in reader.pages[0].extract_text(visitor_text=visitor_text)
    assert "habibi" in reader.pages[1].extract_text(visitor_text=visitor_text)
    assert "حَبيبي" in reader.pages[1].extract_text(visitor_text=visitor_text)
    assert "habibi" in reader.pages[2].extract_text(visitor_text=visitor_text)
    assert "حَبيبي" in reader.pages[2].extract_text(visitor_text=visitor_text)
    assert "habibi" in reader.pages[3].extract_text(visitor_text=visitor_text)
    assert "حَبيبي" in reader.pages[3].extract_text(visitor_text=visitor_text)


@pytest.mark.parametrize(
    ("file_name", "constraints"),
    [
        (
            "inkscape-abc.pdf",
            {
                "A": lambda x, y: 0 < x < 94 and 189 < y < 283,  # In upper left
                "B": lambda x, y: 94 < x < 189 and 94 < y < 189,  # In the center
                "C": lambda x, y: 189 < x < 283 and 0 < y < 94,
            },  # In lower right
        )
    ],
)
def test_visitor_text_matrices(file_name, constraints):
    """
    Checks if the matrices given to the visitor_text function when calling
    `extract_text` on the first page of `file_name` match some given constraints.
    `constraints` is a dictionary mapping a line of text to a constraint that should
    evaluate to `True` on its expected x,y-coordinates.
    """
    reader = PdfReader(RESOURCE_ROOT / file_name)

    lines = []

    def visitor_text(text, cm, tm, font_dict, font_size) -> None:
        ctm = mult(tm, cm)
        x = ctm[4]  # used to tm[4] * cm[0] + tm[5] * cm[2] + cm[4]  # mult(tm, cm)[4]
        y = ctm[
            5
        ]  # used to be tm[4] * cm[1] + tm[5] * cm[3] + cm[5]  # mult(tm, cm)[5]
        lines.append({"text": text, "x": x, "y": y})

    reader.pages[0].extract_text(visitor_text=visitor_text)

    for text, constraint in constraints.items():
        matches = [li for li in lines if li["text"].strip() == text]
        assert len(matches) <= 1, f"Multiple lines match {text}"
        assert len(matches) >= 1, f"No lines match {text}"

        x = matches[0]["x"]
        y = matches[0]["y"]
        assert constraint(x, y), f'Line "{text}" is wrong at x:{x}, y:{y}'
