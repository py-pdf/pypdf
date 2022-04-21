import os

import pytest

from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.errors import PageSizeNotDefinedError
from PyPDF2.generic import RectangleObject

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


def test_writer_clone():
    src = os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf")

    reader = PdfFileReader(src)
    writer = PdfFileWriter()

    writer.cloneDocumentFromReader(reader)
    assert writer.getNumPages() == 4


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
    writer.insertPage(reader_outline.pages[0], 0)
    writer.addBookmarkDestination(page)
    writer.removeLinks()
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

    # TODO: This gives "KeyError: '/Contents'" - is that a bug?
    # writer.removeImages()

    writer.addMetadata({"author": "Martin Thoma"})

    writer.addAttachment("foobar.gif", b"foobarcontent")

    # finally, write "output" to PyPDF2-output.pdf
    tmp_path = "dont_commit_writer.pdf"
    with open(tmp_path, "wb") as output_stream:
        writer.write(output_stream)

    # cleanup
    os.remove(tmp_path)


@pytest.mark.parametrize(
    "input_path,ignoreByteStringObject",
    [
        ("side-by-side-subfig.pdf", False),
        ("reportlab-inline-image.pdf", True),
    ],
)
def test_remove_images(input_path, ignoreByteStringObject):
    pdf_path = os.path.join(RESOURCE_ROOT, input_path)

    reader = PdfFileReader(pdf_path)
    writer = PdfFileWriter()

    page = reader.pages[0]
    writer.insertPage(page, 0)
    writer.removeImages(ignoreByteStringObject=ignoreByteStringObject)

    # finally, write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_writer_removed_image.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    with open(tmp_filename, "rb") as input_stream:
        reader = PdfFileReader(input_stream)
        if input_path == "side-by-side-subfig.pdf":
            assert "Lorem ipsum dolor sit amet" in reader.getPage(0).extractText()

    # Cleanup
    os.remove(tmp_filename)


@pytest.mark.parametrize(
    "input_path,ignoreByteStringObject",
    [
        ("side-by-side-subfig.pdf", False),
        ("side-by-side-subfig.pdf", True),
        ("reportlab-inline-image.pdf", False),
        ("reportlab-inline-image.pdf", True),
    ],
)
def test_remove_text(input_path, ignoreByteStringObject):
    pdf_path = os.path.join(RESOURCE_ROOT, input_path)

    reader = PdfFileReader(pdf_path)
    writer = PdfFileWriter()

    page = reader.pages[0]
    writer.insertPage(page, 0)
    writer.removeText(ignoreByteStringObject=ignoreByteStringObject)

    # finally, write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_writer_removed_text.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

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


def test_fill_form():
    reader = PdfFileReader(os.path.join(RESOURCE_ROOT, "form.pdf"))
    writer = PdfFileWriter()

    page = reader.pages[0]

    writer.addPage(page)

    writer.updatePageFormFieldValues(writer.getPage(0), {"foo": "some filled in text"})

    # write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_filled_pdf.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)


def test_encrypt():
    reader = PdfFileReader(os.path.join(RESOURCE_ROOT, "form.pdf"))
    writer = PdfFileWriter()

    page = reader.pages[0]

    writer.addPage(page)
    writer.encrypt(user_pwd="userpwd", owner_pwd="ownerpwd", use_128bit=False)

    # write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_encrypted.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_add_bookmark():
    reader = PdfFileReader(os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf"))
    writer = PdfFileWriter()

    for page in reader.pages:
        writer.addPage(page)

    bookmark = writer.addBookmark(
        "A bookmark", 1, None, (255, 0, 15), True, True, "/Fit", 200, 0, None
    )
    writer.addBookmark("Another", 2, bookmark, None, False, False, "/Fit", 0, 0, None)

    # write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_bookmark.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_add_named_destination():
    reader = PdfFileReader(os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf"))
    writer = PdfFileWriter()

    for page in reader.pages:
        writer.addPage(page)

    from PyPDF2.pdf import NameObject

    writer.addNamedDestination(NameObject("A named dest"), 2)

    from PyPDF2.pdf import IndirectObject

    assert writer.getNamedDestRoot() == ["A named dest", IndirectObject(7, 0, writer)]

    # write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_named_destination.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_add_uri():
    reader = PdfFileReader(os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf"))
    writer = PdfFileWriter()

    for page in reader.pages:
        writer.addPage(page)

    from PyPDF2.pdf import RectangleObject

    writer.addURI(
        1,
        "http://www.example.com",
        RectangleObject([0, 0, 100, 100]),
        border=[1, 2, 3, [4]],
    )
    writer.addURI(
        2,
        "https://pypdf2.readthedocs.io/en/latest/",
        RectangleObject([20, 30, 50, 80]),
        border=[1, 2, 3],
    )
    writer.addURI(
        3,
        "https://pypdf2.readthedocs.io/en/latest/user/adding-pdf-annotations.html",
        "[ 200 300 250 350 ]",
        border=[0, 0, 0],
    )
    writer.addURI(
        3,
        "https://pypdf2.readthedocs.io/en/latest/user/adding-pdf-annotations.html",
        [100, 200, 150, 250],
        border=[0, 0, 0],
    )

    # write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_uri.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_add_link():
    reader = PdfFileReader(os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf"))
    writer = PdfFileWriter()

    for page in reader.pages:
        writer.addPage(page)

    from PyPDF2.pdf import RectangleObject

    writer.addLink(
        1,
        2,
        RectangleObject([0, 0, 100, 100]),
        border=[1, 2, 3, [4]],
        fit="/Fit",
    )
    writer.addLink(2, 3, RectangleObject([20, 30, 50, 80]), [1, 2, 3], "/FitH", None)
    writer.addLink(
        3,
        0,
        "[ 200 300 250 350 ]",
        [0, 0, 0],
        "/XYZ",
        0,
        0,
        2,
    )
    writer.addLink(
        3,
        0,
        [100, 200, 150, 250],
        border=[0, 0, 0],
    )

    # write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_link.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_io_streams():
    """This is the example from the docs ("Streaming data")."""
    # Arrange
    from io import BytesIO

    filepath = os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf")
    with open(filepath, "rb") as fh:
        bytes_stream = BytesIO(fh.read())

    # Read from bytes stream
    reader = PdfFileReader(bytes_stream)
    assert reader.getNumPages() == 4

    # Write to bytes stream
    writer = PdfFileWriter()
    with BytesIO() as output_stream:
        writer.write(output_stream)


def test_regression_issue670():
    filepath = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    reader = PdfFileReader(filepath, strict=False, overwriteWarnings=False)
    for _ in range(2):
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(reader.getPage(0))
        with open("dont_commit_issue670.pdf", "wb") as f_pdf:
            pdf_writer.write(f_pdf)
