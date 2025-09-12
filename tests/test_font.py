"""Test font-related functionality."""

from pypdf._font import FontDescriptor
from pypdf.generic import DictionaryObject, NameObject


def test_font_descriptor():
    font_res = DictionaryObject({NameObject("/BaseFont"): NameObject("/Helvetica")})
    my_font = FontDescriptor.from_font_resource(font_res)
    assert my_font.family == "Helvetica"
    assert my_font.weight == "Medium"
    assert my_font.ascent == 718
    assert my_font.descent == -207

    test_string = "This is a long sentence. !@%%^€€€. çûįö¶´"
    charwidth = sum(my_font.character_widths[char] for char in test_string)
    assert charwidth == 19251

    font_res = DictionaryObject({NameObject("/BaseFont"): NameObject("/Palatino")})
    my_font = FontDescriptor.from_font_resource(font_res)
    assert my_font.weight == "Unknown"

    font_res = DictionaryObject({NameObject("/BaseFont"): NameObject("/Courier-Bold")})
    my_font = FontDescriptor.from_font_resource(font_res)
    assert my_font.italic_angle == 0
    assert my_font.flags == 33
    assert my_font.bbox == (-113.0, -250.0, 749.0, 801.0)
