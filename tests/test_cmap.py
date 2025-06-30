"""Test the pypdf_cmap module."""
from io import BytesIO
from pathlib import Path

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf._cmap import build_char_map, get_encoding
from pypdf._codecs import charset_encoding
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject, NameObject, NullObject

from . import get_data_from_url

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


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
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)), strict=strict)
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
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)), strict=strict)
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
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    assert within_text in reader.pages[page_nb].extract_text()


@pytest.mark.enable_socket
def test_iss1533():
    reader = PdfReader(BytesIO(get_data_from_url(name="iss1533.pdf")))
    reader.pages[0].extract_text()  # no error
    assert build_char_map("/F", 200, reader.pages[0])[3]["\x01"] == "Ü"


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
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
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
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    assert "《中国能源展望 2060（2024 年版）》编写委员会" in reader.pages[1].extract_text()


@pytest.mark.enable_socket
def test_too_many_differences():
    """Cf #2836"""
    url = (
        "https://github.com/user-attachments/files/16911741/dumb_extract_text_crash.pdf"
    )
    name = "iss2836.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    assert reader.pages[0].extract_text() == ""


@pytest.mark.enable_socket
def test_iss2925():
    url = (
        "https://github.com/user-attachments/files/17621508/2305.09315.pdf"
    )
    name = "iss2925.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    assert "slicing on the PDG to extract the relevant contextual" in reader.pages[3].extract_text()


@pytest.mark.enable_socket
def test_iss2966():
    """Regression test for issue #2966: indirect objects in fonts"""
    url = (
        "https://github.com/user-attachments/files/17904233/repro_out.pdf"
    )
    name = "iss2966.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    assert "Lorem ipsum dolor sit amet" in reader.pages[0].extract_text()


@pytest.mark.enable_socket
def test_binascii_odd_length_string(caplog):
    """Tests for #2216"""
    url = "https://github.com/user-attachments/files/18199642/iss2216.pdf"
    name = "iss2216.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))

    page = reader.pages[0]
    assert "\n(Many other theorems may\n" in page.extract_text()
    assert "Skipping broken line b'143f   143f   10300': Odd-length string\n" in caplog.text


@pytest.mark.enable_socket
def test_standard_encoding(caplog):
    """Tests for #3156"""
    url = "https://github.com/user-attachments/files/18983503/standard-encoding.pdf"
    name = "issue3156.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))

    page = reader.pages[0]
    assert page.extract_text() == "Lorem ipsum"
    assert "Advanced encoding" not in caplog.text


@pytest.mark.enable_socket
def test_function_in_font_widths(caplog):
    """Tests for #3153"""
    url = "https://github.com/user-attachments/files/18945709/Marseille_pypdf_level_0.2._compressed.pdf"
    name = "issue3153.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))

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
