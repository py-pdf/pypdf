import os
import pytest

from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.utils import PageSizeNotDefinedError

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


def test_insert():
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    outline = os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf")

    reader = PdfFileReader(open(pdf_path, "rb"))

    output = PdfFileWriter()
    page = reader.pages[0]
    with pytest.raises(PageSizeNotDefinedError):
        output.addBlankPage()
    output.insertPage(page, 1)
    output.addBlankPage()
    output.insertBlankPage(width=100, height=100)
    # finally, write "output" to PyPDF2-output.pdf
    with open("dont_commit_writer.pdf", "wb") as output_stream:
        output.write(output_stream)
