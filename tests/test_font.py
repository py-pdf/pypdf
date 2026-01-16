"""Test font-related functionality."""
from pathlib import Path

import pytest

from pypdf import PdfReader
from pypdf._font import Font, FontDescriptor
from pypdf.errors import PdfReadError
from pypdf.generic import DictionaryObject, EncodedStreamObject, NameObject

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


def test_font_descriptor():
    font_res = DictionaryObject({
        NameObject("/BaseFont"): NameObject("/Helvetica"),
        NameObject("/Subtype"): NameObject("/Type1")
    })
    my_font = FontDescriptor.from_font_resource(font_res)
    assert my_font.family == "Helvetica"
    assert my_font.weight == "Medium"
    assert my_font.ascent == 718
    assert my_font.descent == -207

    test_string = "This is a long sentence. !@%%^€€€. çûįö¶´"
    charwidth = sum(my_font.character_widths[char] for char in test_string)
    assert charwidth == 19251

    font_res[NameObject("/BaseFont")] = NameObject("/Palatino")
    my_font = FontDescriptor.from_font_resource(font_res)
    assert my_font.weight == "Unknown"

    font_res[NameObject("/BaseFont")] = NameObject("/Courier-Bold")
    my_font = FontDescriptor.from_font_resource(font_res)
    assert my_font.italic_angle == 0
    assert my_font.flags == 33
    assert my_font.bbox == (-113.0, -250.0, 749.0, 801.0)


def test_font_file():
    reader = PdfReader(RESOURCE_ROOT / "multilang.pdf")

    # /FontFile
    font = Font.from_font_resource(reader.pages[0]["/Resources"]["/Font"]["/F2"])
    assert type(font.font_descriptor.font_file) is EncodedStreamObject
    assert len(font.font_descriptor.font_file.get_data()) == 5116

    # /FontFile2
    font_resource = reader.pages[0]["/Resources"]["/Font"]["/F1"]
    font = Font.from_font_resource(font_resource)
    assert type(font.font_descriptor.font_file) is EncodedStreamObject
    assert len(font.font_descriptor.font_file.get_data()) == 28464

    with pytest.raises(PdfReadError) as exception:
        font_resource[NameObject("/FontDescriptor")][NameObject("/FontFile")] = NameObject("xyz")
        font = Font.from_font_resource(font_resource)
    assert "More than one /FontFile" in exception.value.args[0]

    # /FontFile3
    reader = PdfReader(RESOURCE_ROOT / "attachment.pdf")
    font = Font.from_font_resource(reader.pages[0]["/Resources"]["/Font"]["/F1"])
    assert type(font.font_descriptor.font_file) is EncodedStreamObject
    assert len(font.font_descriptor.font_file.get_data()) == 2168
