"""Test the pypdf_cmap module."""
from io import BytesIO

import pytest

from pypdf import PdfReader
from pypdf._cmap import build_char_map
from pypdf.errors import PdfReadWarning

from . import get_pdf_from_url


@pytest.mark.enable_socket()
@pytest.mark.slow()
@pytest.mark.parametrize(
    ("url", "name", "strict"),
    [
        # compute_space_width:
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/923/923406.pdf",
            "tika-923406.pdf",
            False,
        ),
        # _parse_to_unicode_process_rg:
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/959/959173.pdf",
            "tika-959173.pdf",
            False,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/959/959173.pdf",
            "tika-959173.pdf",
            True,
        ),
        # issue #1718:
        (
            "https://github.com/py-pdf/pypdf/files/10983477/Ballinasloe_WS.pdf",
            "iss1718.pdf",
            False,
        ),
    ],
)
def test_text_extraction_slow(caplog, url: str, name: str, strict: bool):
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)), strict=strict)
    for page in reader.pages:
        page.extract_text()
    assert caplog.text == ""


@pytest.mark.enable_socket()
@pytest.mark.parametrize(
    ("url", "name", "strict"),
    [
        # bfchar_on_2_chars: issue #1293
        (
            "https://github.com/xyegithub/myBlog/raw/main/posts/c94b2364/paper_pdfs/ImageClassification/"
            "2007%2CASurveyofImageClassificationBasedTechniques.pdf",
            "ASurveyofImageClassificationBasedTechniques.pdf",
            False,
        ),
        # L40, get_font_width_from_default
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/908/908104.pdf",
            "tika-908104.pdf",
            False,
        ),
        # multiline_bfrange / regression test for issue #1285:
        (
            "https://github.com/alexanderquispe/1REI05/raw/main/reports/report_1/"
            "The%20lean%20times%20in%20the%20Peruvian%20economy.pdf",
            "The%20lean%20times%20in%20the%20Peruvian%20economy.pdf",
            False,
        ),
        (
            "https://github.com/yxj-HGNwmb5kdp8ewr/yxj-HGNwmb5kdp8ewr.github.io/raw/master/files/"
            "Giacalone%20Llobell%20Jaeger%20(2022)%20Food%20Qual%20Prefer.pdf",
            "Giacalone.pdf",
            False,
        ),
    ],
)
def test_text_extraction_fast(caplog, url: str, name: str, strict: bool):
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)), strict=strict)
    for page in reader.pages:
        page.extract_text()
    assert caplog.text == ""


@pytest.mark.enable_socket()
def test_parse_encoding_advanced_encoding_not_implemented():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/957/957144.pdf"
    name = "tika-957144.pdf"

    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    with pytest.warns(PdfReadWarning, match="Advanced encoding .* not implemented yet"):
        for page in reader.pages:
            page.extract_text()


@pytest.mark.enable_socket()
def test_ascii_charset():
    # iss #1312
    url = "https://github.com/py-pdf/pypdf/files/9472500/main.pdf"
    name = "ascii charset.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    assert "/a" not in reader.pages[0].extract_text()


@pytest.mark.enable_socket()
@pytest.mark.parametrize(
    ("url", "name", "page_nb"),
    [
        (
            "https://github.com/py-pdf/pypdf/files/9667138/cmap1370.pdf",
            "cmap1370.pdf",
            0,
        ),
        ("https://github.com/py-pdf/pypdf/files/9712729/02voc.pdf", "02voc.pdf", 2),
    ],
    ids=["iss1370", "iss1379"],
)
def test_text_extraction_of_specific_pages(url: str, name: str, page_nb: int):
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    reader.pages[page_nb].extract_text()


@pytest.mark.enable_socket()
def test_iss1533():
    url = "https://github.com/py-pdf/pypdf/files/10376149/iss1533.pdf"
    name = "iss1533.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    reader.pages[0].extract_text()  # no error
    assert build_char_map("/F", 200, reader.pages[0])[3]["\x01"] == "Ü"
