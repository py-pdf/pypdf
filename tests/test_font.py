"""Test font-related functionality."""
import os
import re
import subprocess
import sys
import unicodedata
from io import BytesIO

import pytest
from fontTools.ttLib import TTFont

from pypdf import PdfReader, PdfWriter
from pypdf._cmap import _parse_to_unicode
from pypdf._font import Font, FontDescriptor
from pypdf.errors import LimitReachedError, PdfReadError
from pypdf.generic import ArrayObject, DictionaryObject, EncodedStreamObject, NameObject, NumberObject, RectangleObject
from pypdf.generic._appearance_stream import BaseStreamConfig, TextStreamAppearance

from . import RESOURCE_ROOT


def test_font_descriptor():
    font_res = DictionaryObject({
        NameObject("/BaseFont"): NameObject("/Helvetica"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/Encoding"): NameObject("/WinAnsiEncoding")
    })
    my_font = Font.from_font_resource(font_res)
    assert my_font.font_descriptor.family == "Helvetica"
    assert my_font.font_descriptor.weight == "Medium"
    assert my_font.font_descriptor.ascent == 718
    assert my_font.font_descriptor.descent == -207

    test_string = "This is a long sentence. !@%%^€€€. çûiö¶´"
    reverse_map = {char: byte for byte, char in my_font.encoding.items()}
    encoded_string = ([chr(reverse_map[char]) for char in test_string])
    charwidth = my_font.get_text_width(encoded_string)
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


@pytest.mark.parametrize("w_array", [[45], [45, 65]])
def test_collect_cid_character_widths_truncated_w(w_array):
    # A /W array that ends mid-entry must not read past its bounds.
    d_font = DictionaryObject({
        NameObject("/Subtype"): NameObject("/CIDFontType2"),
        NameObject("/W"): ArrayObject(NumberObject(v) for v in w_array),
    })
    font_res = DictionaryObject({
        NameObject("/Subtype"): NameObject("/Type0"),
        NameObject("/BaseFont"): NameObject("/Foo"),
        NameObject("/DescendantFonts"): ArrayObject([d_font]),
    })
    Font.from_font_resource(font_res)


@pytest.mark.parametrize("bbox", [
    pytest.param(ArrayObject([NumberObject(0), NumberObject(0), NumberObject(100)]), id="too-short"),
    pytest.param(ArrayObject(NumberObject(v) for v in range(6)), id="too-long"),
    pytest.param(ArrayObject([NameObject("/x"), NumberObject(0), NumberObject(1), NumberObject(2)]), id="non-numeric"),
    pytest.param(NumberObject(0), id="not-a-sequence"),
])
def test_font_descriptor_malformed_bbox(bbox):
    # A /FontBBox that is not four numbers must fall back to the default
    # bounding box instead of crashing text extraction.
    font_res = DictionaryObject({
        NameObject("/BaseFont"): NameObject("/Foo"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/FontDescriptor"): DictionaryObject({
            NameObject("/FontBBox"): bbox,
        }),
    })
    font = Font.from_font_resource(font_res)
    assert font.font_descriptor.bbox == FontDescriptor._DEFAULT_BBOX


@pytest.mark.parametrize("bbox", [
    pytest.param(ArrayObject([NumberObject(0), NumberObject(0)]), id="too-short"),
    pytest.param(ArrayObject([NameObject("/x"), NumberObject(0), NumberObject(1), NumberObject(2)]), id="non-numeric"),
])
def test_type3_font_malformed_bbox(bbox):
    # Type3 font without a /FontDescriptor but carrying a malformed /FontBBox.
    font_res = DictionaryObject({
        NameObject("/BaseFont"): NameObject("/Foo"),
        NameObject("/Subtype"): NameObject("/Type3"),
        NameObject("/ToUnicode"): NumberObject(0),
        NameObject("/FontBBox"): bbox,
    })
    font = Font.from_font_resource(font_res)
    assert font.font_descriptor.bbox == FontDescriptor._DEFAULT_BBOX


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
                # Test zero units per em
                tt_font_object["head"].unitsPerEm = 0
                tt_font_object.save(crippled_font_data)
                with pytest.raises(PdfReadError, match=r"invalid unitsPerEm"):
                    Font.from_truetype_font_file(crippled_font_data)
                tt_font_object["head"].unitsPerEm = 2048

                # Test various missing tables
                del tt_font_object["name"]
                del tt_font_object["OS/2"]
                del tt_font_object["post"]
                crippled_font_data.seek(0)
                tt_font_object.save(crippled_font_data)
                font = Font.from_truetype_font_file(crippled_font_data)

                # Test raising AttributeError in _get_typographic_maps due to missing cmap table
                del tt_font_object["cmap"]
                crippled_font_data.seek(0)
                tt_font_object.save(crippled_font_data)
                crippled_font_data_value = crippled_font_data.getvalue()
                font.font_descriptor.font_file.set_data(crippled_font_data_value)
                font._get_typographic_maps()

                # Test raising PdfReadError in from_truetype_font_file due to missing cmap table
                with pytest.raises(PdfReadError, match=r"Font file does not have a cmap table"):
                    Font.from_truetype_font_file(crippled_font_data)

                # Test raising TTLibError in _get_typographic_maps due to corrupt font data
                garbage_bytes = b"CORRUPT_HEADER!!" + crippled_font_data_value[16:]
                font.font_descriptor.font_file.set_data(garbage_bytes)
                font._get_typographic_maps()


def test_font_as_font_resource():
    writer = PdfWriter(RESOURCE_ROOT / "fontsampler.pdf")
    font_resources = writer.pages[0]["/Resources"]["/Font"]
    font_data = font_resources["/F7"]["/DescendantFonts"][0]["/FontDescriptor"]["/FontFile2"].get_data()
    font = Font.from_truetype_font_file(BytesIO(font_data))
    font._add_to_writer(writer, font_resources, NameObject("/" + font.name))


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


def test_font__collect_cid_character_widths__limits():
    # Format 1 exceeding length.
    d_font = DictionaryObject({
        NameObject("/W"): ArrayObject([
            NumberObject(1), ArrayObject([NumberObject(42)] * 100_000),
        ])
    })
    current_widths = {}
    with pytest.raises(
            expected_exception=LimitReachedError, match=r"^CID width range too large: 100000 > 65536\.$"
    ):
        Font._collect_cid_character_widths(d_font=d_font, current_widths=current_widths)
    assert current_widths == {}

    # Format 1 exceeding entry count.
    d_font = DictionaryObject({
        NameObject("/W"): ArrayObject([
            NumberObject(1), ArrayObject([NumberObject(42)] * 55_000),
            NumberObject(1), ArrayObject([NumberObject(13)] * 60_000),
        ])
    })
    current_widths = {}
    with pytest.raises(
            expected_exception=LimitReachedError, match=r"^Too many character widths: 115000 > 100000\.$"
    ):
        Font._collect_cid_character_widths(d_font=d_font, current_widths=current_widths)
    assert current_widths == {
        chr(character_index): 42
        for character_index in range(1, 55_001, 1)
    }

    # Format 2 exceeding length.
    d_font = DictionaryObject({
        NameObject("/W"): ArrayObject([
            NumberObject(1), NumberObject(100_000), NumberObject(42),
        ])
    })
    current_widths = {}
    with pytest.raises(
            expected_exception=LimitReachedError, match=r"^CID width range too large: 100000 > 65536\.$"
    ):
        Font._collect_cid_character_widths(d_font=d_font, current_widths=current_widths)
    assert current_widths == {}

    # Format 2 exceeding entry count.
    d_font = DictionaryObject({
        NameObject("/W"): ArrayObject([
            NumberObject(1), NumberObject(55_000), NumberObject(42),
            NumberObject(1), NumberObject(60_000), NumberObject(13),
        ])
    })
    current_widths = {}
    with pytest.raises(
            expected_exception=LimitReachedError, match=r"^Too many character widths: 115000 > 100000\.$"
    ):
        Font._collect_cid_character_widths(d_font=d_font, current_widths=current_widths)
    assert current_widths == {
        chr(character_index): 42
        for character_index in range(1, 55_001, 1)
    }

    # Inverted range.
    d_font = DictionaryObject({
        NameObject("/W"): ArrayObject([
            NumberObject(13), NumberObject(1), NumberObject(42),
        ])
    })
    current_widths = {}
    with pytest.raises(
            expected_exception=LimitReachedError, match=r"^Invalid CID width range: 13\.\.2\.$"
    ):
        Font._collect_cid_character_widths(d_font=d_font, current_widths=current_widths)
    assert current_widths == {}


def test_simple_font_reverse_cmap_from_character_map():
    pdf_path = RESOURCE_ROOT / "side-by-side-subfig.pdf"
    reader = PdfReader(pdf_path)
    extracted_text = reader.pages[0].extract_text()
    font = Font.from_font_resource(reader.pages[0]["/Resources"]["/Font"]["/F33"])

    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    writer.pages[0]["/Resources"][NameObject("/Font")] = DictionaryObject()
    font._add_to_writer(writer, writer.pages[0]["/Resources"]["/Font"], NameObject(f"/{font.name}"))
    appearance_stream = TextStreamAppearance(
        layout=BaseStreamConfig(rectangle=RectangleObject((0.0, 0.0, 512, 692))),
        text=extracted_text,
        font=font,
        font_resource=writer.pages[0]["/Resources"]["/Font"][f"/{font.name}"],
        is_multiline=True
    )
    writer._add_apstream_object(
        page,
        appearance_stream,
        "LoremIpsum",
        x_offset=100,
        y_offset=692
    )

    stream = BytesIO()
    writer.write(stream)
    stream.seek(0)

    reader2 = PdfReader(stream)
    assert extracted_text == reader2.pages[0].extract_text()


def test__create_widths_list_and_unicode_stream():
    font = Font.from_core_font_name("Helvetica")
    # Make sure that we have some encoding difference so that we will include a
    # ToUnicode CMap in a font resource.
    font.encoding[255] = font.encoding[0]
    # Assert that the ToUnicode CMap can be parsed and reflects the original encoding.
    map_dict, _ = _parse_to_unicode(font.as_font_resource())
    assert all(
        map_dict[chr(chr_code)] == unicodedata.normalize("NFKC", unipoint)
        for chr_code, unipoint in font.encoding.items()
    )
    # Test that we observe CMAP_MAX_ENTRIES_PER_GROUP; we're using a core font which
    # has 256 characters. Hence, we should have two groups of 100 bfchar lines
    # and one group with the remaining 56 bfchar lines.
    _widths_list, to_unicode_stream = font._create_widths_list_and_unicode_stream()
    assert all(
        val in ("56", "100") for val in re.findall(r"([0-9]*) beginbfchar", to_unicode_stream.get_data().decode())
    )
