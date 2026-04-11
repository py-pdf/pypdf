"""Test font-related functionality."""
from io import BytesIO

import pytest

from pypdf import PdfReader
from pypdf._font import HAS_FONTTOOLS, Font
from pypdf.errors import PdfReadError
from pypdf.generic import DictionaryObject, EncodedStreamObject, NameObject

from . import RESOURCE_ROOT


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


def test_font_from_font_file():
    if not HAS_FONTTOOLS:
        with pytest.raises(ImportError) as excinfo:
            Font.from_truetype_font_file(BytesIO(b""))
        assert "The 'fontTools' library is required to use 'from_truetype_font_file'" in str(excinfo.value)
        return
    reader = PdfReader(RESOURCE_ROOT / "fontsampler.pdf")
    font_resources = reader.pages[0]["/Resources"]["/Font"]
    for font_resource in font_resources:
        font_data = font_resources[font_resource]["/DescendantFonts"][0]["/FontDescriptor"]["/FontFile2"].get_data()
        font = Font.from_truetype_font_file(BytesIO(font_data))
        if font_resource == "/F1":
            assert font.font_descriptor.flags == 33
            assert len(font.character_map) == 872
        if font_resource == "/F2":
            assert font.font_descriptor.flags == 32
        if font_resource == "/F3":
            assert font.font_descriptor.flags == 98
        if font_resource == "/F4":
            assert len(font.character_map) == 697
            assert len(font.character_widths) == 698
