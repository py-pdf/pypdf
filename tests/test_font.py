"""Test font-related functionality."""
import os
import subprocess
import sys
from io import BytesIO

import pytest
from fontTools.ttLib import TTFont

from pypdf import PdfReader
from pypdf._font import Font
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
    assert isinstance(font.font_descriptor.font_file, EncodedStreamObject)
    assert len(font.font_descriptor.font_file.get_data()) == 5116

    # /FontFile2
    font_resource = reader.pages[0]["/Resources"]["/Font"]["/F1"]
    font = Font.from_font_resource(font_resource)
    assert isinstance(font.font_descriptor.font_file, EncodedStreamObject)
    assert len(font.font_descriptor.font_file.get_data()) == 28464

    with pytest.raises(PdfReadError, match=r"^More than one /FontFile found in .+$"):
        font_resource[NameObject("/FontDescriptor")][NameObject("/FontFile")] = NameObject("xyz")
        font = Font.from_font_resource(font_resource)

    # /FontFile3
    reader = PdfReader(RESOURCE_ROOT / "attachment.pdf")
    font = Font.from_font_resource(reader.pages[0]["/Resources"]["/Font"]["/F1"])
    assert isinstance(font.font_descriptor.font_file, EncodedStreamObject)
    assert len(font.font_descriptor.font_file.get_data()) == 2168


def test_font_from_font_file():
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
        if font_resource == "/F6":
            crippled_font_data = BytesIO()
            with TTFont(BytesIO(font_data)) as tt_font_object:
                del tt_font_object["name"]
                del tt_font_object["OS/2"]
                del tt_font_object["post"]
                tt_font_object.save(crippled_font_data)
                font = Font.from_truetype_font_file(crippled_font_data)
                crippled_font_data.seek(0)
                del tt_font_object["cmap"]
                tt_font_object.save(crippled_font_data)
                with pytest.raises(PdfReadError, match=r"Font file does not have a cmap table"):
                    Font.from_truetype_font_file(crippled_font_data)


def test_font_from_font_file_no_fonttools(tmp_path):
    env = os.environ.copy()
    env["COVERAGE_PROCESS_START"] = "pyproject.toml"

    source_file = tmp_path / "script.py"
    source_file.write_text(
        """
import sys
from io import BytesIO

import pytest

sys.modules["fontTools.ttLib"] = None
from pypdf._font import Font

with pytest.raises(ImportError, match=r"^The 'fontTools' library is required to use 'from_truetype_font_file'$"):
    Font.from_truetype_font_file(BytesIO(b""))
"""
    )

    try:
        env["PYTHONPATH"] = "." + os.pathsep + env["PYTHONPATH"]
    except KeyError:
        env["PYTHONPATH"] = "."
    result = subprocess.run(  # noqa: S603
        [sys.executable, source_file],
        capture_output=True,
        env=env,
    )
    assert result.returncode == 0
    assert result.stdout == b""
