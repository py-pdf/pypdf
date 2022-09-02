from io import BytesIO

import pytest

from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadWarning

from . import get_pdf_from_url


def test_compute_space_width():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/923/923406.pdf"
    name = "tika-923406.pdf"

    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for page in reader.pages:
        page.extract_text()


def test_parse_to_unicode_process_rg():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/959/959173.pdf"
    name = "tika-959173.pdf"

    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for page in reader.pages:
        page.extract_text()

    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)), strict=True)
    for page in reader.pages:
        page.extract_text()


def test_parse_encoding_advanced_encoding_not_implemented():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/957/957144.pdf"
    name = "tika-957144.pdf"

    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    with pytest.warns(PdfReadWarning, match="Advanced encoding .* not implemented yet"):
        for page in reader.pages:
            page.extract_text()


def test_get_font_width_from_default():  # L40
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/908/908104.pdf"
    name = "tika-908104.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for page in reader.pages:
        page.extract_text()


def test_bfchar_on_2_chars():
    # iss #1293
    url = "https://github.com/xyegithub/myBlog/raw/main/posts/c94b2364/paper_pdfs/ImageClassification/2007%2CASurveyofImageClassificationBasedTechniques.pdf"
    name = "ASurveyofImageClassificationBasedTechniques.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for page in reader.pages:
        page.extract_text()


def test_ascii_charset():
    # iss #1312
    url = "https://github.com/py-pdf/PyPDF2/files/9472500/main.pdf"
    name = "ascii charset.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    assert "/a" not in reader.pages[0].extract_text()
