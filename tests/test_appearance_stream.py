"""Test the pypdf.generic._appearance_stream module."""
import os
import re
import subprocess
import sys
import unicodedata
from unittest import mock

from pypdf import PdfWriter
from pypdf._font import Font
from pypdf.generic import RectangleObject
from pypdf.generic._appearance_stream import BaseStreamConfig, TextStreamAppearance

from . import RESOURCE_ROOT


def test_comb():
    layout=BaseStreamConfig(rectangle=(0.0, 0.0, 197.285, 18.455))
    font_size = 10.0
    text = "01234567"
    max_length = 10
    is_comb = True
    appearance_stream = TextStreamAppearance(
        layout=layout, text=text, font_size=font_size, is_comb=is_comb, max_length=max_length
    )
    assert appearance_stream.get_data() == (
        b"q\n/Tx BMC \nq\n2 1 193.285 16.455 re\nW\nBT\n/Helv 10.0 Tf 0 g\n"
        b"7.084250000000001 5.637499999999999 Td\n(0) Tj\n"
        b"19.7285 0.0 Td\n(1) Tj\n"
        b"19.728500000000004 0.0 Td\n(2) Tj\n"
        b"19.728499999999997 0.0 Td\n(3) Tj\n"
        b"19.728499999999997 0.0 Td\n(4) Tj\n"
        b"19.728499999999997 0.0 Td\n(5) Tj\n"
        b"19.72850000000001 0.0 Td\n(6) Tj\n"
        b"19.728499999999997 0.0 Td\n(7) Tj\nET\nQ\nEMC\nQ\n"
    )

    layout.rectangle = (0.0, 0.0, 20.852, 20.84)
    text = "AA"
    max_length = 1
    appearance_stream = TextStreamAppearance(
        layout=layout, text=text, font_size=font_size, is_comb=is_comb, max_length=max_length
    )
    assert appearance_stream.get_data() == (
        b"q\n/Tx BMC \nq\n2 1 16.852 18.84 re\nW\nBT\n/Helv 10.0 Tf 0 g\n7.091 6.83 Td\n(A) Tj\nET\nQ\nEMC\nQ\n"
    )


def test_scale_text():
    layout=BaseStreamConfig(rectangle=(0, 0, 9.1, 55.4))
    font_size = 10.1
    text = "Hello World"
    is_multiline = False
    appearance_stream = TextStreamAppearance(
        layout=layout, text=text, font_size=font_size, is_multiline=is_multiline
    )
    assert b"10.1 Tf" in appearance_stream.get_data()

    text = "This is a very very long sentence that probably will scale below the minimum font size"
    font_size = 0.0
    appearance_stream = TextStreamAppearance(
        layout=layout, text=text, font_size=font_size, is_multiline=is_multiline
    )
    assert b"4.0 Tf" in appearance_stream.get_data()

    layout.rectangle = (0, 0, 160, 360)
    font_size = 0.0
    text = """Welcome to pypdf
pypdf is a free and open source pure-python PDF library capable of splitting, merging, cropping, and
transforming the pages of PDF files. It can also add custom data, viewing options, and passwords to PDF
files. pypdf can retrieve text and metadata from PDFs as well.

See pdfly for a CLI application that uses pypdf to interact with PDFs.
    """
    is_multiline = True
    appearance_stream = TextStreamAppearance(
        layout=layout, text=text, font_size=font_size, is_multiline=is_multiline
    )
    assert b"12 Tf" in appearance_stream.get_data()
    assert b"pypdf is a free and open" in appearance_stream.get_data()

    layout.rectangle = (0, 0, 160, 160)
    appearance_stream = TextStreamAppearance(
        layout=layout, text=text, font_size=font_size, is_multiline=is_multiline
    )
    assert b"9.8 Tf" in appearance_stream.get_data()

    layout.rectangle = (0, 0, 160, 12)
    appearance_stream = TextStreamAppearance(
        layout=layout, text=text, font_size=font_size, is_multiline=is_multiline
    )
    text = """Option A
Option B
Option C
Option D
"""
    selection = "Option A"
    assert b"4.0 Tf" in appearance_stream.get_data()

    text = "pneumonoultramicroscopicsilicovolcanoconiosis"
    appearance_stream = TextStreamAppearance(
        layout=layout, text=text, selection=selection, font_size=font_size, is_multiline=is_multiline
    )
    assert b"7.3 Tf" in appearance_stream.get_data()

    layout.rectangle = (0, 0, 10, 100)
    text = "OneWord"
    appearance_stream = TextStreamAppearance(
        layout=layout, text=text, font_size=font_size, is_multiline=is_multiline
    )
    assert b"OneWord" in appearance_stream.get_data()


def test_appearance_stream_rtl():
    writer = PdfWriter(RESOURCE_ROOT / "fontsampler.pdf")
    layout = BaseStreamConfig(
        rectangle=RectangleObject([0, 0, 250, 30]),
        border_width=0
    )
    test_string = "!مرحبا بالعالم Hello World!"
    font_name = "/F7"
    font_resource = writer.pages[0]["/Resources"]["/Font"][font_name]
    font = Font.from_font_resource(font_resource)
    reverse_cmap, encoding_cmap = font._get_typographic_maps()
    unshaped_test_glyphs = [reverse_cmap[char] for char in test_string]
    hex_unshaped_test_glyphs = "".join(encoding_cmap[glyph_id].hex() for glyph_id in unshaped_test_glyphs)
    shaped_test_string = "!\ufee3\ufeae\ufea3\ufe92\ufe8e \ufe91\ufe8e\ufedf\ufecc\ufe8e\ufedf\ufee2 Hello World!"
    assert unicodedata.normalize("NFKC", shaped_test_string) == test_string
    shaped_test_glyphs = [reverse_cmap[char] for char in shaped_test_string]
    # Reverse the arabic part of the test string to enable comparison with the RTL-supported case.
    hex_shaped_test_glyphs = "".join(
        encoding_cmap[glyph_id].hex()
        for glyph_id in shaped_test_glyphs[:1] + shaped_test_glyphs[1:14][::-1] + shaped_test_glyphs[14:]
    )
    appearance = TextStreamAppearance(
        layout=layout,
        text=test_string,
        font_resource=font_resource,
        font=font,
        font_name=font_name,
        font_size=12.0,
        font_color="0 g",
        is_multiline=False
    )
    hex_glyphs_rtl_enabled = re.findall("<(.+?)>", appearance.get_data().decode())[0]
    assert hex_shaped_test_glyphs == hex_glyphs_rtl_enabled

    # RTL support disabled
    with mock.patch("pypdf.generic._appearance_stream.HAS_RTL_SUPPORT", False):
        appearance = TextStreamAppearance(
            layout=layout,
            text=test_string,
            font_resource=font_resource,
            font=font,
            font_name=font_name,
            font_size=12.0,
            font_color="0 g",
            is_multiline=False
        )
        hex_glyphs_rtl_disabled = re.findall("<(.+?)>", appearance.get_data().decode())[0]
    assert hex_unshaped_test_glyphs == hex_glyphs_rtl_disabled
    # The hex glyph sequences should be different when RTL support is enabled vs disabled
    assert hex_glyphs_rtl_enabled != hex_glyphs_rtl_disabled

    # fontTools support disabled
    with mock.patch("pypdf._font.HAS_FONTTOOLS", False):
        appearance = TextStreamAppearance(
            layout=layout,
            text=test_string,
            font_resource=font_resource,
            font=font,
            font_name=font_name,
            font_size=12.0,
            font_color="0 g",
            is_multiline=False
        )
        hex_glyphs_rtl_enabled_fonttools_disabled  = re.findall("<(.+?)>", appearance.get_data().decode())[0]
    assert hex_shaped_test_glyphs != hex_glyphs_rtl_enabled_fonttools_disabled


def test_appearance_stream__no_arabic_reshaper(tmp_path):
    env = os.environ.copy()
    env["COVERAGE_PROCESS_START"] = "pyproject.toml"

    source_file = tmp_path / "script.py"
    source_file.write_text(
        """
import sys
from io import BytesIO

import pytest

sys.modules["arabic_reshaper"] = None
from pypdf.generic._appearance_stream import TextStreamAppearance, HAS_RTL_SUPPORT

assert HAS_RTL_SUPPORT is False
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
