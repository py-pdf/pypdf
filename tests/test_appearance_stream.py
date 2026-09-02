"""Test the pypdf.generic._appearance_stream module."""
import os
import re
import subprocess
import sys
from unittest import mock

import pytest

from pypdf import PdfWriter, Transformation
from pypdf._font import HAS_FONTTOOLS, Font
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    RectangleObject,
)
from pypdf.generic._appearance_stream import (
    HAS_RTL_SUPPORT,
    BaseStreamAppearance,
    BaseStreamConfig,
    TextStreamAppearance,
)

from . import RESOURCE_ROOT


def test_comb():
    layout=BaseStreamConfig(rectangle=RectangleObject((0.0, 0.0, 197.285, 18.455)))
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

    layout.rectangle = RectangleObject((0.0, 0.0, 20.852, 20.84))
    text = "AA"
    max_length = 1
    appearance_stream = TextStreamAppearance(
        layout=layout, text=text, font_size=font_size, is_comb=is_comb, max_length=max_length
    )
    assert appearance_stream.get_data() == (
        b"q\n/Tx BMC \nq\n2 1 16.852 18.84 re\nW\nBT\n/Helv 10.0 Tf 0 g\n7.091 6.83 Td\n(A) Tj\nET\nQ\nEMC\nQ\n"
    )


def test_scale_text():
    layout=BaseStreamConfig(rectangle=RectangleObject((0, 0, 9.1, 55.4)))
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

    layout.rectangle = RectangleObject((0, 0, 160, 360))
    font_size = 0.0
    text = """Welcome to pypdf!
أهلاً بكم في pypdf!
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
    assert b"/Span << /ActualText" in appearance_stream.get_data()

    layout.rectangle = RectangleObject((0, 0, 160, 160))
    appearance_stream = TextStreamAppearance(
        layout=layout, text=text, font_size=font_size, is_multiline=is_multiline
    )
    assert b"9.6 Tf" in appearance_stream.get_data()

    layout.rectangle = RectangleObject((0, 0, 160, 12))
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

    layout.rectangle = RectangleObject((0, 0, 10, 100))
    text = "OneWord"
    appearance_stream = TextStreamAppearance(
        layout=layout, text=text, font_size=font_size, is_multiline=is_multiline
    )
    assert b"OneWord" in appearance_stream.get_data()

@pytest.mark.skipif(
    not HAS_RTL_SUPPORT or not HAS_FONTTOOLS,
    reason="Requires arabic-reshaper, python-bidi and fontTools"
)
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
    # The regex returns two matches. The first matches the text in /Span << /ActualText <[group 0]> >> BDC
    # The second match concerns the encoded text data.
    [hex_actual_text, hex_glyphs_rtl_enabled] = re.findall("<([a-zA-Z0-9]+?)> ", appearance.get_data().decode())
    assert bytes.fromhex(hex_actual_text).decode("utf-16-be") == "\ufeff" + test_string
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
        [hex_glyphs_rtl_disabled] = re.findall("^<(.+?)>", appearance.get_data().decode(), re.MULTILINE)
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
        [hex_glyphs_rtl_enabled_fonttools_disabled] = re.findall(
            "^<(.+?)>", appearance.get_data().decode(), re.MULTILINE
        )
    assert hex_shaped_test_glyphs != hex_glyphs_rtl_enabled_fonttools_disabled


@pytest.mark.parametrize("module", ["arabic_reshaper", "bidi"])
def test_appearance_stream__no_rtl_support(module, tmp_path):
    env = os.environ.copy()
    env["COVERAGE_PROCESS_START"] = "pyproject.toml"

    source_file = tmp_path / "script.py"
    source_file.write_text(
        f"""
import sys
from io import BytesIO

import pytest

sys.modules["{module}"] = None
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


@pytest.mark.parametrize(
    ("rotation", "outcome"),
    [
        (0, None),
        (90, [0.0, 1, -1, 0.0, 20, 0.0]),
        (180, [-1, 0.0, 0.0, -1, 400, 20]),
        (270, [0.0, -1, 1, 0.0, 0.0, 400]),
        (360, None),
    ]
)
def test_base_stream_config_rotation(rotation, outcome):
    layout = BaseStreamConfig(
        rectangle=RectangleObject([0, 0, 400, 20]),
        border_width=1,
        rotation=rotation,
    )
    appearance = BaseStreamAppearance(layout=layout)
    assert appearance.get("/Matrix", None) == outcome


def test_merge_transformed_page_annotation_with_ap_but_no_normal_state():
    """/AP present but missing /N (malformed, but must not raise) is a no-op
    for the appearance transform -- /Rect still moves normally.
    """
    src_writer = PdfWriter()
    src_page = src_writer.add_blank_page(width=200, height=200)
    annotation = DictionaryObject()
    annotation[NameObject("/Type")] = NameObject("/Annot")
    annotation[NameObject("/Subtype")] = NameObject("/Square")
    annotation[NameObject("/Rect")] = RectangleObject((20, 20, 120, 70))
    annotation[NameObject("/AP")] = DictionaryObject()  # no /N key
    src_writer.add_annotation(0, annotation)

    dest_writer = PdfWriter()
    dest_page = dest_writer.add_blank_page(width=200, height=200)
    dest_page.merge_transformed_page(src_page, Transformation().translate(10, 5))

    merged = dest_page["/Annots"][0].get_object()
    assert tuple(round(float(x), 6) for x in merged["/Rect"]) == (30.0, 25.0, 130.0, 75.0)


def test_merge_transformed_page_annotation_with_malformed_normal_state():
    """/N resolving to something other than a stream or a state dict (a
    malformed PDF) must be skipped, not raise.
    """
    src_writer = PdfWriter()
    src_page = src_writer.add_blank_page(width=200, height=200)
    annotation = DictionaryObject()
    annotation[NameObject("/Type")] = NameObject("/Annot")
    annotation[NameObject("/Subtype")] = NameObject("/Square")
    annotation[NameObject("/Rect")] = RectangleObject((20, 20, 120, 70))
    annotation[NameObject("/AP")] = DictionaryObject({NameObject("/N"): NumberObject(5)})
    src_writer.add_annotation(0, annotation)

    dest_writer = PdfWriter()
    dest_page = dest_writer.add_blank_page(width=200, height=200)
    dest_page.merge_transformed_page(src_page, Transformation().translate(10, 5))

    merged = dest_page["/Annots"][0].get_object()
    assert tuple(round(float(x), 6) for x in merged["/Rect"]) == (30.0, 25.0, 130.0, 75.0)
    assert merged["/AP"]["/N"] == 5


def test_merge_transformed_page_updates_annotation_appearance_matrix():
    """
    An annotation's /Rect is repositioned/resized by the merge transform, but
    per the appearance-stream algorithm (PDF 2.0, 12.5.5) a viewer fits the
    appearance's /BBox into /Rect with an axis-aligned scale only, never a
    rotation. Leaving /AP /N's /Matrix untouched under a rotating transform
    therefore stretches the original, unrotated appearance content into the
    new, differently-shaped /Rect instead of rotating it. The transform must
    be composed into the appearance's own /Matrix as well.
    """
    src_writer = PdfWriter()
    src_page = src_writer.add_blank_page(width=200, height=200)

    ap_stream = DecodedStreamObject()
    ap_stream.set_data(b"0 0 m 100 50 l S")
    ap_stream[NameObject("/Type")] = NameObject("/XObject")
    ap_stream[NameObject("/Subtype")] = NameObject("/Form")
    ap_stream[NameObject("/BBox")] = ArrayObject(
        [FloatObject(0), FloatObject(0), FloatObject(100), FloatObject(50)]
    )
    ap_ref = src_writer._add_object(ap_stream)

    annotation = DictionaryObject()
    annotation[NameObject("/Type")] = NameObject("/Annot")
    annotation[NameObject("/Subtype")] = NameObject("/Square")
    annotation[NameObject("/Rect")] = RectangleObject((20, 20, 120, 70))
    annotation[NameObject("/AP")] = DictionaryObject({NameObject("/N"): ap_ref})
    src_writer.add_annotation(0, annotation)

    dest_writer = PdfWriter()
    dest_page = dest_writer.add_blank_page(width=200, height=200)
    transform = Transformation().rotate(90).translate(200, 0)
    dest_page.merge_transformed_page(src_page, transform)

    merged_ap = dest_page["/Annots"][0].get_object()["/AP"]["/N"].get_object()
    # A pure 90 degree rotation + translate composed onto an identity
    # starting matrix: (0, 1, -1, 0, 200, 0).
    matrix = tuple(round(float(x), 6) for x in merged_ap["/Matrix"])
    assert matrix == (0.0, 1.0, -1.0, 0.0, 200.0, 0.0)
    # The appearance stream's own local geometry (/BBox) is untouched; only
    # /Matrix carries the transform, consistent with how content streams and
    # /Rect are already handled elsewhere in this function.
    assert tuple(merged_ap["/BBox"]) == (0, 0, 100, 50)


def test_merge_transformed_page_composes_existing_annotation_matrix():
    """An annotation that already has its own /Matrix must have the merge
    transform composed on top of it, not overwrite it outright.
    """
    src_writer = PdfWriter()
    src_page = src_writer.add_blank_page(width=200, height=200)

    ap_stream = DecodedStreamObject()
    ap_stream.set_data(b"0 0 m 100 50 l S")
    ap_stream[NameObject("/Type")] = NameObject("/XObject")
    ap_stream[NameObject("/Subtype")] = NameObject("/Form")
    ap_stream[NameObject("/BBox")] = ArrayObject(
        [FloatObject(0), FloatObject(0), FloatObject(100), FloatObject(50)]
    )
    # Pre-existing 2x horizontal scale.
    ap_stream[NameObject("/Matrix")] = ArrayObject(
        [FloatObject(v) for v in (2, 0, 0, 1, 0, 0)]
    )
    ap_ref = src_writer._add_object(ap_stream)

    annotation = DictionaryObject()
    annotation[NameObject("/Type")] = NameObject("/Annot")
    annotation[NameObject("/Subtype")] = NameObject("/Square")
    annotation[NameObject("/Rect")] = RectangleObject((0, 0, 200, 50))
    annotation[NameObject("/AP")] = DictionaryObject({NameObject("/N"): ap_ref})
    src_writer.add_annotation(0, annotation)

    dest_writer = PdfWriter()
    dest_page = dest_writer.add_blank_page(width=200, height=200)
    # Translate-only this time, to isolate composition order from rotation.
    transform = Transformation().translate(10, 5)
    dest_page.merge_transformed_page(src_page, transform)

    merged_ap = dest_page["/Annots"][0].get_object()["/AP"]["/N"].get_object()
    matrix = tuple(round(float(x), 6) for x in merged_ap["/Matrix"])
    # (2, 0, 0, 1, 0, 0) composed with a (10, 5) translation: the scale is
    # preserved and the translation is appended, not scaled by it.
    assert matrix == (2.0, 0.0, 0.0, 1.0, 10.0, 5.0)


def test_merge_transformed_page_annotation_without_appearance_stream():
    """Annotations with no /AP at all (the common case) must merge exactly
    as before -- only /Rect moves, and nothing raises.
    """
    src_writer = PdfWriter()
    src_page = src_writer.add_blank_page(width=200, height=200)
    annotation = DictionaryObject()
    annotation[NameObject("/Type")] = NameObject("/Annot")
    annotation[NameObject("/Subtype")] = NameObject("/Square")
    annotation[NameObject("/Rect")] = RectangleObject((20, 20, 120, 70))
    src_writer.add_annotation(0, annotation)

    dest_writer = PdfWriter()
    dest_page = dest_writer.add_blank_page(width=200, height=200)
    transform = Transformation().rotate(90).translate(200, 0)
    dest_page.merge_transformed_page(src_page, transform)

    merged = dest_page["/Annots"][0].get_object()
    assert "/AP" not in merged
    assert tuple(round(float(x), 6) for x in merged["/Rect"]) == (130.0, 20.0, 180.0, 120.0)


def test_merge_transformed_page_annotation_with_multi_state_appearance():
    """Widget annotations with multiple states (e.g. checkboxes) store /AP /N
    as a dict of named sub-streams rather than a single stream. Every state's
    /Matrix must be updated, not just the first, and nothing should raise.
    """
    src_writer = PdfWriter()
    src_page = src_writer.add_blank_page(width=200, height=200)

    states = {}
    for name in ("/Off", "/Yes"):
        state_stream = DecodedStreamObject()
        state_stream.set_data(b"0 0 m 100 50 l S")
        state_stream[NameObject("/Type")] = NameObject("/XObject")
        state_stream[NameObject("/Subtype")] = NameObject("/Form")
        state_stream[NameObject("/BBox")] = ArrayObject(
            [FloatObject(0), FloatObject(0), FloatObject(100), FloatObject(50)]
        )
        states[NameObject(name)] = src_writer._add_object(state_stream)

    annotation = DictionaryObject()
    annotation[NameObject("/Type")] = NameObject("/Annot")
    annotation[NameObject("/Subtype")] = NameObject("/Widget")
    annotation[NameObject("/Rect")] = RectangleObject((20, 20, 120, 70))
    annotation[NameObject("/AP")] = DictionaryObject(
        {NameObject("/N"): DictionaryObject(states)}
    )
    src_writer.add_annotation(0, annotation)

    dest_writer = PdfWriter()
    dest_page = dest_writer.add_blank_page(width=200, height=200)
    transform = Transformation().rotate(90).translate(200, 0)
    dest_page.merge_transformed_page(src_page, transform)

    merged_states = dest_page["/Annots"][0].get_object()["/AP"]["/N"]
    assert set(merged_states.keys()) == {"/Off", "/Yes"}
    for state in merged_states.values():
        matrix = tuple(round(float(x), 6) for x in state.get_object()["/Matrix"])
        assert matrix == (0.0, 1.0, -1.0, 0.0, 200.0, 0.0)
