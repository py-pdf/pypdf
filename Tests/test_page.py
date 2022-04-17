import os

import pytest

from PyPDF2 import PdfFileReader

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


@pytest.mark.parametrize(
    "pdf_path, password",
    [
        ("crazyones.pdf", None),
        ("attachment.pdf", None),
        # ("side-by-side-subfig.pdf", None),
        (
            "libreoffice-writer-password.pdf",
            "openpassword",
        ),
        ("imagemagick-images.pdf", None),
        ("imagemagick-lzw.pdf", None),
        ("reportlab-inline-image.pdf", None),
    ],
)
def test_page_operations(pdf_path, password):
    """
    This test just checks if the operation throws an exception.

    This should be done way more thoroughly: It should be checked if the
    output is as expected.
    """
    pdf_path = os.path.join(RESOURCE_ROOT, pdf_path)
    reader = PdfFileReader(pdf_path)

    if password:
        reader.decrypt(password)

    page = reader.pages[0]
    page.mergeRotatedScaledPage(page, 90, 1, 1)
    page.mergeScaledTranslatedPage(page, 1, 1, 1)
    page.mergeRotatedScaledTranslatedPage(page, 90, 1, 1, 1, 1)
    page.addTransformation([1, 0, 0, 0, 0, 0])
    page.scale(2, 2)
    page.scaleBy(0.5)
    page.scaleTo(100, 100)
    page.compressContentStreams()
    page.extractText()


@pytest.mark.parametrize(
    "pdf_path, password",
    [
        (os.path.join(RESOURCE_ROOT, "crazyones.pdf"), None),
        (os.path.join(RESOURCE_ROOT, "attachment.pdf"), None),
        (os.path.join(RESOURCE_ROOT, "side-by-side-subfig.pdf"), None),
        (
            os.path.join(RESOURCE_ROOT, "libreoffice-writer-password.pdf"),
            "openpassword",
        ),
    ],
)
def test_compress_content_streams(pdf_path, password):
    reader = PdfFileReader(pdf_path)
    if password:
        reader.decrypt(password)
    for page in reader.pages:
        page.compressContentStreams()
