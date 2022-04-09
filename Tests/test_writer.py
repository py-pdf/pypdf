import os
import pytest

from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.utils import PageSizeNotDefinedError
from PyPDF2.generic import IndirectObject, RectangleObject

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


def test_writer_operations():
    """
    This test just checks if the operation throws an exception.

    This should be done way more thoroughly: It should be checked if the
    output is as expected.
    """
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    pdf_outline_path = os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf")

    reader = PdfFileReader(open(pdf_path, "rb"))
    reader_outline = PdfFileReader(open(pdf_outline_path, "rb"))

    output = PdfFileWriter()
    page = reader.pages[0]
    with pytest.raises(PageSizeNotDefinedError):
        output.addBlankPage()
    output.insertPage(page, 1)
    output.removeText()
    output.insertPage(reader_outline.pages[0], 0)
    output.addBookmarkDestination(page)
    output.addBookmark("A bookmark", 0)
    # output.addNamedDestination("A named destination", 1)
    output.removeLinks()
    # assert output.getNamedDestRoot() == ['A named destination', IndirectObject(9, 0, output)]
    output.addBlankPage()
    output.addURI(2, "https://example.com", RectangleObject([0, 0, 100, 100]))
    output.addLink(2, 1, RectangleObject([0, 0, 100, 100]))
    assert output.getPageLayout() is None
    output.setPageLayout("SinglePage")
    assert output.getPageLayout() == "SinglePage"
    assert output.getPageMode() is None
    output.setPageMode("UseNone")
    assert output.getPageMode() == "UseNone"
    output.insertBlankPage(width=100, height=100)
    output.insertBlankPage()  # without parameters

    # This gives "KeyError: '/Contents'" - is that a bug?
    # output.removeImages()

    output.addMetadata({"author": "Martin Thoma"})

    output.addAttachment("foobar.gif", b"foobarcontent")

    # finally, write "output" to PyPDF2-output.pdf
    with open("dont_commit_writer.pdf", "wb") as output_stream:
        output.write(output_stream)


def test_remove_images():
    pdf_path = os.path.join(RESOURCE_ROOT, "side-by-side-subfig.pdf")

    reader = PdfFileReader(open(pdf_path, "rb"))
    output = PdfFileWriter()

    page = reader.pages[0]
    output.insertPage(page, 0)
    output.removeImages()

    # finally, write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_writer_removed_image.pdf"
    with open(tmp_filename, "wb") as output_stream:
        output.write(output_stream)

    with open(tmp_filename, "rb") as input_stream:
        reader = PdfFileReader(input_stream)
        assert "Lorem ipsum dolor sit amet" in reader.getPage(0).extractText()

    # Cleanup
    os.remove(tmp_filename)
