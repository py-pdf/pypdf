"""Test the pypdf_cmap module."""
import sys
from io import BytesIO

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf._cmap import get_encoding, parse_bfchar, parse_bfrange
from pypdf._codecs import charset_encoding
from pypdf._font import Font
from pypdf.errors import LimitReachedError
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    EncodedStreamObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    StreamObject,
    TextStringObject,
)

from . import RESOURCE_ROOT, get_data_from_url


@pytest.mark.enable_socket
@pytest.mark.slow
@pytest.mark.parametrize(
    ("url", "name", "strict"),
    [
        # compute_space_width:
        (
            None,
            "tika-923406.pdf",
            False,
        ),
        # _parse_to_unicode_process_rg:
        (
            None,
            "tika-959173.pdf",
            False,
        ),
        (
            None,
            "tika-959173.pdf",
            True,
        ),
        # issue #1718:
        (
            None,
            "iss1718.pdf",
            False,
        ),
    ],
)
def test_text_extraction_slow(caplog, url: str, name: str, strict: bool):
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)), strict=strict)
    for page in reader.pages:
        page.extract_text()
    assert caplog.text == ""


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name", "strict"),
    [
        # bfchar_on_2_chars: issue #1293
        (
            None,
            "ASurveyofImageClassificationBasedTechniques.pdf",
            False,
        ),
        # L40, get_font_width_from_default
        (
            None,
            "tika-908104.pdf",
            False,
        ),
        # multiline_bfrange / regression test for issue #1285:
        (
            None,
            "The%20lean%20times%20in%20the%20Peruvian%20economy.pdf",
            False,
        ),
        (
            None,
            "Giacalone.pdf",
            False,
        ),
    ],
)
def test_text_extraction_fast(caplog, url: str, name: str, strict: bool):
    """Text extraction runs without exceptions or warnings"""
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)), strict=strict)
    for page in reader.pages:
        page.extract_text()
    assert caplog.text == ""


@pytest.mark.enable_socket
def test_parse_encoding_advanced_encoding_not_implemented(caplog):
    reader = PdfReader(BytesIO(get_data_from_url(name="tika-957144.pdf")))
    for page in reader.pages:
        page.extract_text()
    # The correctly spelled encoding is /WinAnsiEncoding
    assert "Advanced encoding /WinAnsEncoding not implemented yet" in caplog.text


@pytest.mark.enable_socket
def test_ascii_charset():
    # Issue #1312
    reader = PdfReader(BytesIO(get_data_from_url(name="ascii charset.pdf")))
    assert "/a" not in reader.pages[0].extract_text()


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name", "page_nb", "within_text"),
    [
        (
            None,
            "cmap1370.pdf",
            0,
            "",
        ),
        (
            None,
            "02voc.pdf",
            2,
            "Document delineation and character sequence decoding",
        ),
    ],
    ids=["iss1370", "iss1379"],
)
def test_text_extraction_of_specific_pages(
    url: str, name: str, page_nb: int, within_text
):
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))
    assert within_text in reader.pages[page_nb].extract_text()


@pytest.mark.enable_socket
def test_iss1533():
    reader = PdfReader(BytesIO(get_data_from_url(name="iss1533.pdf")))
    reader.pages[0].extract_text()  # no error
    font = Font.from_font_resource(reader.pages[0]["/Resources"]["/Font"]["/F"])
    assert font.character_map["\x01"] == "Ü"
    assert isinstance(font.font_descriptor.font_file, EncodedStreamObject)
    assert font.font_descriptor.font_file["/Subtype"] == "/CIDFontType0C"


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name", "page_index", "within_text", "caplog_text"),
    [
        (
            None,
            "tstUCS2.pdf",
            1,
            ["2 / 12", "S0490520090001", "于博"],
            "",
        ),
        (
            None,
            "tst-GBK_EUC.pdf",
            0,
            ["NJA", "中华男科学杂志"],
            "Multiple definitions in dictionary at byte 0x5cb42 for key /MediaBox\n",
        ),
    ],
)
def test_cmap_encodings(caplog, url, name, page_index, within_text, caplog_text):
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))
    extracted = reader.pages[page_index].extract_text()  # no error
    for contained in within_text:
        assert contained in extracted
    assert caplog_text in caplog.text


@pytest.mark.enable_socket
def test_latex():
    reader = PdfReader(BytesIO(get_data_from_url(name="math_latex.pdf")))
    txt = reader.pages[0].extract_text()  # no error
    for pat in ("α", "β", "γ", "ϕ", "φ", "ℏ", "∫", "∂", "·", "×"):
        assert pat in txt
    # actually the ϕ and φ seems to be crossed in latex


@pytest.mark.enable_socket
def test_unixxx_glyphs():
    reader = PdfReader(BytesIO(get_data_from_url(name="unixxx_glyphs.pdf")))
    txt = reader.pages[0].extract_text()  # no error
    for pat in ("闫耀庭", "龚龑", "张江水", "1′′.2"):
        assert pat in txt


@pytest.mark.enable_socket
def test_cmap_compute_space_width():
    # issue 2137
    # original file URL:
    # url = "https://arxiv.org/pdf/2005.05909.pdf"
    # URL from github issue is too long to pass code type check, use original arxiv URL instead
    # url = "https://github.com/py-pdf/pypdf/files/12489914/Morris.et.al.-.2020.-.TextAttack.A.Framework.for.Adversarial.Attacks.Data.Augmentation.and.Adversarial.Training.in.NLP.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(name="TextAttack_paper.pdf")))
    reader.pages[0].extract_text()  # no error


@pytest.mark.enable_socket
def test_tabs_in_cmap():
    """Issue #2173"""
    reader = PdfReader(BytesIO(get_data_from_url(name="iss2173.pdf")))
    reader.pages[0].extract_text()


@pytest.mark.enable_socket
def test_ignoring_non_put_entries():
    """Issue #2290"""
    reader = PdfReader(BytesIO(get_data_from_url(name="iss2290.pdf")))
    reader.pages[0].extract_text()


@pytest.mark.enable_socket
def test_eten_b5():
    """Issue #2356"""
    reader = PdfReader(BytesIO(get_data_from_url(name="iss2290.pdf")))
    reader.pages[0].extract_text().startswith("1/7 \n富邦新終身壽險")


def test_missing_entries_in_cmap():
    """
    Issue #2702: this issue is observed on damaged pdfs
    use of this file in test has been discarded as too slow/long
    we will create the same error from crazyones
    """
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    p = reader.pages[0]
    p["/Resources"]["/Font"]["/F1"][NameObject("/ToUnicode")] = IndirectObject(
        99999999, 0, reader
    )
    p.extract_text()


def test_null_missing_width():
    """For coverage of #2792"""
    writer = PdfWriter(RESOURCE_ROOT / "crazyones.pdf")
    page = writer.pages[0]
    ft = page["/Resources"]["/Font"]["/F1"]
    ft[NameObject("/Widths")] = ArrayObject()
    ft["/FontDescriptor"][NameObject("/MissingWidth")] = NullObject()
    page.extract_text()


@pytest.mark.enable_socket
def test_unigb_utf16():
    """Cf #2812"""
    url = (
        "https://github.com/user-attachments/files/16767536/W020240105322424121296.pdf"
    )
    name = "iss2812.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))
    assert "《中国能源展望 2060（2024 年版）》编写委员会" in reader.pages[1].extract_text()


@pytest.mark.enable_socket
def test_too_many_differences():
    """Cf #2836"""
    url = (
        "https://github.com/user-attachments/files/16911741/dumb_extract_text_crash.pdf"
    )
    name = "iss2836.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))
    assert reader.pages[0].extract_text() == ""


@pytest.mark.enable_socket
def test_iss2925():
    url = (
        "https://github.com/user-attachments/files/17621508/2305.09315.pdf"
    )
    name = "iss2925.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))
    assert "slicing on the PDG to extract the relevant contextual" in reader.pages[3].extract_text()


@pytest.mark.enable_socket
def test_iss2966():
    """Regression test for issue #2966: indirect objects in fonts"""
    url = (
        "https://github.com/user-attachments/files/17904233/repro_out.pdf"
    )
    name = "iss2966.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))
    assert "Lorem ipsum dolor sit amet" in reader.pages[0].extract_text()


@pytest.mark.enable_socket
def test_binascii_odd_length_string(caplog):
    """Tests for #2216"""
    url = "https://github.com/user-attachments/files/18199642/iss2216.pdf"
    name = "iss2216.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))

    page = reader.pages[0]
    assert "\n(Many other theorems may\n" in page.extract_text()
    if sys.version_info >= (3, 15):
        assert "Skipping broken line b'143f   143f   10300': Odd number of hexadecimal digits\n" in caplog.text
    else:
        assert "Skipping broken line b'143f   143f   10300': Odd-length string\n" in caplog.text


@pytest.mark.enable_socket
def test_standard_encoding(caplog):
    """Tests for #3156"""
    url = "https://github.com/user-attachments/files/18983503/standard-encoding.pdf"
    name = "issue3156.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))

    page = reader.pages[0]
    assert page.extract_text() == "Lorem ipsum"
    assert "Advanced encoding" not in caplog.text


@pytest.mark.enable_socket
def test_function_in_font_widths(caplog):
    """Tests for #3153"""
    url = "https://github.com/user-attachments/files/18945709/Marseille_pypdf_level_0.2._compressed.pdf"
    name = "issue3153.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))

    page = reader.pages[455]
    assert "La vulnérabilité correspond aux conséquences potentielles" in page.extract_text()
    assert "Expected numeric value for width, got {'/Bounds': [0.25, 0.25]," in caplog.text


def test_get_encoding__encoding_value_is_none():
    ft = DictionaryObject()
    ft[NameObject("/Encoding")] = NullObject()
    assert get_encoding(ft) == (
        dict(zip(range(256), charset_encoding["/StandardEncoding"])),
        {}
    )


def _type1_font(font_file_data: bytes) -> DictionaryObject:
    font_file = DecodedStreamObject()
    font_file.set_data(font_file_data)
    font_descriptor = DictionaryObject()
    font_descriptor[NameObject("/FontFile")] = font_file
    ft = DictionaryObject()
    ft[NameObject("/Subtype")] = NameObject("/Type1")
    ft[NameObject("/FontDescriptor")] = font_descriptor
    return ft


def test_get_encoding__type1_font_file_without_encoding():
    # Clear part of the embedded Type1 program has no /Encoding section.
    ft = _type1_font(b"%!PS-AdobeFont\n/FontName /Foo def\neexec\nbinary")
    assert get_encoding(ft) == ("charmap", {})


def test_get_encoding__type1_font_file_truncated_dup_line():
    # A "dup" entry missing the glyph name must be skipped, not crash.
    ft = _type1_font(
        b"/Encoding 256 array\ndup\ndup 65\ndup 97 /a put\nreadonly def\neexec\n"
    )
    _encoding, character_map = get_encoding(ft)
    assert character_map == {"a": "a"}


def test_parse_bfchar(caplog):
    map_dict = {}
    int_entry = []
    parse_bfchar(line=b"057e   1337", map_dict=map_dict, int_entry=int_entry)
    parse_bfchar(line=b"056e   1f310", map_dict=map_dict, int_entry=int_entry)

    assert map_dict == {-1: 2, "ծ": "", "վ": "ጷ"}
    assert int_entry == [1406, 1390]
    if sys.version_info >= (3, 15):
        assert caplog.messages == ["Got invalid hex string: Odd number of hexadecimal digits (b'1f310')"]
    else:
        assert caplog.messages == ["Got invalid hex string: Odd-length string (b'1f310')"]


def test_parse_bfrange__iteration_limit():
    writer = PdfWriter()

    to_unicode = StreamObject()
    to_unicode.set_data(
        b"beginbfrange\n"
        b"<00000000> <001FFFFF> <00000000>\n"
        b"endbfrange\n"
    )
    font = writer._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
        NameObject("/ToUnicode"): to_unicode,
    }))

    page = writer.add_blank_page(width=100, height=100)
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({
            NameObject("/F1"): font.indirect_reference,
        })
    })

    # Case without list, exceeding list directly.
    with pytest.raises(
            expected_exception=LimitReachedError, match=r"^Maximum /ToUnicode size limit reached: 2097152 > 100000\.$"
    ):
        _ = page.extract_text()

    # Use a pre-filled dummy list to simulate multiple calls where the upper bound does
    # not overflow, but the overall size does. Case without list.
    int_entry = [0] * 99_999
    map_dict = {}
    with pytest.raises(
            expected_exception=LimitReachedError, match=r"^Maximum /ToUnicode size limit reached: 165535 > 100000\.$"
    ):
        _ = parse_bfrange(line=b"0000 FFFF 0000", map_dict=map_dict, int_entry=int_entry, multiline_rg=None)
    assert map_dict == {-1: 2}

    # Exceeding from previous call.
    int_entry.append(1)
    map_dict = {}
    with pytest.raises(
            expected_exception=LimitReachedError, match=r"^Maximum /ToUnicode size limit reached: 100001 > 100000\.$"
    ):
        _ = parse_bfrange(line=b"00000000 00000000 00000000", map_dict=map_dict, int_entry=int_entry, multiline_rg=None)
    assert map_dict == {-1: 4}

    # multiline_rg
    int_entry = [0] * 99_995
    map_dict = {-1: 1}
    with pytest.raises(
            expected_exception=LimitReachedError, match=r"^Maximum /ToUnicode size limit reached: 100001 > 100000\.$"
    ):
        _ = parse_bfrange(
            line=b"0020  0021  0022  0023  0024  0025  0026  2019",
            map_dict=map_dict, int_entry=int_entry, multiline_rg=(32, 251)
        )
    assert map_dict == {-1: 1, " ": " ", "!": "!", '"': '"', "#": "#", "$": "$"}

    # No multiline_rg, but list.
    int_entry = [0] * 99_995
    map_dict = {}
    with pytest.raises(
            expected_exception=LimitReachedError, match=r"^Maximum /ToUnicode size limit reached: 100001 > 100000\.$"
    ):
        _ = parse_bfrange(
            line=b"01 8A [ FFFD FFFD FFFD FFFF FFAB AAAA BBBB",
            map_dict=map_dict, int_entry=int_entry, multiline_rg=None
        )
    assert map_dict == {-1: 1, "\x01": "�", "\x02": "�", "\x03": "�", "\x04": "\uffff", "\x05": "ﾫ"}


def test_parse_bfchar__iteration_limit():
    int_entry = [0] * 99_995
    map_dict = {}
    with pytest.raises(
            expected_exception=LimitReachedError, match=r"^Maximum /ToUnicode size limit reached: 100002 > 100000\.$"
    ):
        parse_bfchar(
            line=b"0003   0020   0008   0025   0009   0026   000A   0027   000B   0028   000C   0029   000D   002A",
            map_dict=map_dict, int_entry=int_entry,
        )
    assert map_dict == {}


def _make_japanese_cmap_pdf(cmap_name: str, encoding: str) -> bytes:
    """Minimal PDF with a CIDFont using *cmap_name* as /Encoding, no /ToUnicode."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)

    cid_font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/CIDFontType2"),
        NameObject("/BaseFont"): NameObject("/HeiseiMin-W3"),
        NameObject("/CIDSystemInfo"): DictionaryObject({
            NameObject("/Registry"): TextStringObject("Adobe"),
            NameObject("/Ordering"): TextStringObject("Japan1"),
            NameObject("/Supplement"): NumberObject(2),
        }),
        NameObject("/DW"): NumberObject(1000)
    })
    cid_font_ref = writer._add_object(cid_font)

    type0_font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type0"),
        NameObject("/BaseFont"): NameObject("/HeiseiMin-W3"),
        NameObject("/Encoding"): NameObject(cmap_name),
        NameObject("/DescendantFonts"): ArrayObject([cid_font_ref])
    })
    type0_font_ref = writer._add_object(type0_font)

    type1_font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
        NameObject("/Encoding"): NameObject("/WinAnsiEncoding")
    })
    type1_font_ref = writer._add_object(type1_font)

    char_hex = "日本語テスト".encode(encoding).hex().upper()
    content_data = (
        "BT\n/F0 14 Tf\n72 720 Td\n(Hello ASCII) Tj\n"
        f"0 -28 Td\n/F1 14 Tf\n<{char_hex}> Tj\nET\n"
    ).encode("latin-1")
    content_stream = DecodedStreamObject()
    content_stream.set_data(content_data)
    content_ref = writer._add_object(content_stream)

    page.update({
        NameObject("/Contents"): content_ref,
        NameObject("/Resources"): DictionaryObject({
            NameObject("/Font"): DictionaryObject({
                NameObject("/F0"): type1_font_ref,
                NameObject("/F1"): type0_font_ref
            })
        })
    })

    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()


@pytest.mark.parametrize(
    ("cmap_name", "python_codec"),
    [
        ("/90ms-RKSJ-H", "cp932"),
        ("/90ms-RKSJ-V", "cp932"),
        ("/UniJIS-UTF16-H", "utf-16-be"),
        ("/UniJIS-UTF16-V", "utf-16-be"),
    ],
    ids=["90ms-RKSJ-H", "90ms-RKSJ-V", "UniJIS-UTF16-H", "UniJIS-UTF16-V"],
)
def test_japanese_cmap_encodings(cmap_name: str, python_codec: str, caplog) -> None:
    """Japanese predefined CMaps must be decoded correctly. Resolves #3799."""
    pdf_bytes = _make_japanese_cmap_pdf(cmap_name, python_codec)
    reader = PdfReader(BytesIO(pdf_bytes))
    text = reader.pages[0].extract_text()
    assert "日本語テスト" in text, f"Japanese text garbled for {cmap_name}"
    assert "Hello ASCII"  in text, f"ASCII baseline broken for {cmap_name}"
    assert "Advanced encoding" not in caplog.text
