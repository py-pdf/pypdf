"""Test font-related functionality."""
from pathlib import Path

import pytest

from pypdf import PdfReader
from pypdf._font import Font
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
    my_font = Font.from_font_resource(font_res)
    assert my_font.font_descriptor.family == "Helvetica"
    assert my_font.font_descriptor.weight == "Medium"
    assert my_font.font_descriptor.ascent == 718
    assert my_font.font_descriptor.descent == -207

    test_string = "This is a long sentence. !@%%^€€€. çûįö¶´"
    charwidth = my_font.text_width(test_string)
    assert charwidth == 19251

    font_res[NameObject("/BaseFont")] = NameObject("/Palatino")
    my_font = Font.from_font_resource(font_res)
    assert my_font.font_descriptor.weight == "Unknown"

    font_res[NameObject("/BaseFont")] = NameObject("/Courier-Bold")
    my_font = Font.from_font_resource(font_res)
    assert my_font.font_descriptor.italic_angle == 0
    assert my_font.font_descriptor.flags == 33
    assert my_font.font_descriptor.bbox == (-113.0, -250.0, 749.0, 801.0)
    font_descriptor_resource = my_font.font_descriptor.as_font_descriptor_resource()
    assert font_descriptor_resource == {
        "/Type": "/FontDescriptor",
        "/FontName": "/Courier-Bold",
        "/Flags": 33,
        "/FontBBox": [-113, -250, 749, 801],
        "/ItalicAngle": 0.0,
        "/Ascent": 629,
        "/Descent": -157,
        "/CapHeight": 562,
        "/XHeight": 439
    }


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

    with pytest.raises(PdfReadError, match=r"^More than one /FontFile found in .+$"):
        font_resource[NameObject("/FontDescriptor")][NameObject("/FontFile")] = NameObject("xyz")
        font = Font.from_font_resource(font_resource)

    # /FontFile3
    reader = PdfReader(RESOURCE_ROOT / "attachment.pdf")
    font = Font.from_font_resource(reader.pages[0]["/Resources"]["/Font"]["/F1"])
    assert type(font.font_descriptor.font_file) is EncodedStreamObject
    assert len(font.font_descriptor.font_file.get_data()) == 2168
