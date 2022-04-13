import os

from PyPDF2 import PdfFileReader

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


def test_page_operations():
    """
    This test just checks if the operation throws an exception.

    This should be done way more thoroughly: It should be checked if the
    output is as expected.
    """
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    reader = PdfFileReader(pdf_path)
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
