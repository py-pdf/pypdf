import os

import pytest

from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.errors import PageSizeNotDefinedError
from PyPDF2.generic import RectangleObject

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

    reader = PdfFileReader(pdf_path)
    reader_outline = PdfFileReader(pdf_outline_path)

    writer = PdfFileWriter()
    page = reader.pages[0]
    with pytest.raises(PageSizeNotDefinedError) as exc:
        writer.addBlankPage()
    assert exc.value.args == ()
    writer.insertPage(page, 1)
    writer.removeText()
    writer.insertPage(reader_outline.pages[0], 0)
    writer.addBookmarkDestination(page)
    writer.addBookmark("A bookmark", 0)
    # output.addNamedDestination("A named destination", 1)
    writer.removeLinks()
    # assert output.getNamedDestRoot() == ['A named destination', IndirectObject(9, 0, output)]
    writer.addBlankPage()
    writer.addURI(2, "https://example.com", RectangleObject([0, 0, 100, 100]))
    writer.addLink(2, 1, RectangleObject([0, 0, 100, 100]))
    assert writer.getPageLayout() is None
    writer.setPageLayout("SinglePage")
    assert writer.getPageLayout() == "SinglePage"
    assert writer.getPageMode() is None
    writer.setPageMode("UseNone")
    assert writer.getPageMode() == "UseNone"
    writer.insertBlankPage(width=100, height=100)
    writer.insertBlankPage()  # without parameters

    # This gives "KeyError: '/Contents'" - is that a bug?
    # output.removeImages()

    writer.addMetadata({"author": "Martin Thoma"})

    writer.addAttachment("foobar.gif", b"foobarcontent")

    # finally, write "output" to PyPDF2-output.pdf
    tmp_path = "dont_commit_writer.pdf"
    with open(tmp_path, "wb") as output_stream:
        writer.write(output_stream)

    # cleanup
    os.remove(tmp_path)


def test_remove_images():
    pdf_path = os.path.join(RESOURCE_ROOT, "side-by-side-subfig.pdf")

    reader = PdfFileReader(pdf_path)
    writer = PdfFileWriter()

    page = reader.pages[0]
    writer.insertPage(page, 0)
    writer.removeImages()

    # finally, write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_writer_removed_image.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    with open(tmp_filename, "rb") as input_stream:
        reader = PdfFileReader(input_stream)
        assert "Lorem ipsum dolor sit amet" in reader.getPage(0).extractText()

    # Cleanup
    os.remove(tmp_filename)


def test_write_metadata():
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")

    reader = PdfFileReader(pdf_path)
    writer = PdfFileWriter()

    for page in reader.pages:
        writer.addPage(page)

    metadata = reader.getDocumentInfo()
    writer.addMetadata(metadata)

    writer.addMetadata({"/Title": "The Crazy Ones"})

    # finally, write data to PyPDF2-output.pdf
    tmp_filename = "dont_commit_writer_added_metadata.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Check if the title was set
    reader = PdfFileReader(tmp_filename)
    metadata = reader.getDocumentInfo()
    assert metadata.get("/Title") == "The Crazy Ones"

    # Cleanup
    os.remove(tmp_filename)
