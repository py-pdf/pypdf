"""Tests for the string and byte operands accepted by text extraction."""

import pytest

from pypdf._text_extraction._text_extractor import TextExtraction
from pypdf.generic import ByteStringObject, TextStringObject
from pypdf.generic._font import Font


@pytest.mark.parametrize(
    ("operand", "encoding"),
    [
        ("A é", "latin-1"),
        (TextStringObject("A é"), "latin-1"),
        (b"A \xe9", "latin-1"),
        (ByteStringObject(b"A \xe9"), "latin-1"),
        (b"\x00A\x00 \x00\xe9", "utf-16-be"),
        (b"\x01 \x02", {1: "A", 2: "é"}),
        (ByteStringObject(b"\x01 \x02"), {1: "A", 2: "é"}),
    ],
)
def test_tj_string_and_byte_operands(operand, encoding) -> None:
    extractor = TextExtraction()
    extractor.font = Font(name="Test", encoding=encoding)

    extractor.process_operation(b"Tj", [operand])

    assert extractor.text == "A é"
    assert extractor.output == ""
    assert extractor.rtl_dir is False
    assert extractor._actual_str_size == {
        "str_widths": 15000.0,
        "str_height": 12.0,
    }


@pytest.mark.parametrize("operands", [[], [None], [42], [b""], [""]])
def test_tj_empty_and_unsupported_operands(operands) -> None:
    extractor = TextExtraction()

    extractor.process_operation(b"Tj", operands)

    assert extractor.text == ""
    assert extractor.output == ""
    assert extractor._actual_str_size["str_widths"] == 0.0
