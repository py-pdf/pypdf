from io import BytesIO

from PyPDF2 import PdfReader

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
