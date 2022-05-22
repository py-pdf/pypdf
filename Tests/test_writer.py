import os

import pytest

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.errors import PageSizeNotDefinedError
from PyPDF2.generic import RectangleObject

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


def test_writer_clone():
    src = os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf")

    reader = PdfReader(src)
    writer = PdfWriter()

    writer.clone_document_from_reader(reader)
    assert writer._get_num_pages() == 4


def test_writer_operations():
    """
    This test just checks if the operation throws an exception.

    This should be done way more thoroughly: It should be checked if the
    output is as expected.
    """
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    pdf_outline_path = os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf")

    reader = PdfReader(pdf_path)
    reader_outline = PdfReader(pdf_outline_path)

    writer = PdfWriter()
    page = reader.pages[0]
    with pytest.raises(PageSizeNotDefinedError) as exc:
        writer.add_blank_page()
    assert exc.value.args == ()
    writer.insert_page(page, 1)
    writer.insert_page(reader_outline.pages[0], 0)
    writer.add_bookmark_destination(page)
    writer.remove_links()
    writer.add_blank_page()
    writer.add_uri(2, "https://example.com", RectangleObject([0, 0, 100, 100]))
    writer.add_link(2, 1, RectangleObject([0, 0, 100, 100]))
    assert writer._get_page_layout() is None
    writer._set_page_layout("SinglePage")
    assert writer._get_page_layout() == "SinglePage"
    assert writer._get_page_mode() is None
    writer.set_page_mode("UseNone")
    assert writer._get_page_mode() == "UseNone"
    writer.insert_blank_page(width=100, height=100)
    writer.insert_blank_page()  # without parameters

    # TODO: This gives "KeyError: '/Contents'" - is that a bug?
    # writer.removeImages()

    writer.add_metadata({"author": "Martin Thoma"})

    writer.add_attachment("foobar.gif", b"foobarcontent")

    # finally, write "output" to PyPDF2-output.pdf
    tmp_path = "dont_commit_writer.pdf"
    with open(tmp_path, "wb") as output_stream:
        writer.write(output_stream)

    # cleanup
    os.remove(tmp_path)


@pytest.mark.parametrize(
    ("input_path", "ignoreByteStringObject"),
    [
        ("side-by-side-subfig.pdf", False),
        ("reportlab-inline-image.pdf", True),
    ],
)
def test_remove_images(input_path, ignoreByteStringObject):
    pdf_path = os.path.join(RESOURCE_ROOT, input_path)

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    page = reader.pages[0]
    writer.insert_page(page, 0)
    writer.remove_images(ignore_byte_string_object=ignoreByteStringObject)

    # finally, write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_writer_removed_image.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    with open(tmp_filename, "rb") as input_stream:
        reader = PdfReader(input_stream)
        if input_path == "side-by-side-subfig.pdf":
            extracted_text = reader._get_page(0).extract_text()
            assert "Lorem ipsum dolor sit amet" in extracted_text

    # Cleanup
    os.remove(tmp_filename)


@pytest.mark.parametrize(
    ("input_path", "ignoreByteStringObject"),
    [
        ("side-by-side-subfig.pdf", False),
        ("side-by-side-subfig.pdf", True),
        ("reportlab-inline-image.pdf", False),
        ("reportlab-inline-image.pdf", True),
    ],
)
def test_remove_text(input_path, ignoreByteStringObject):
    pdf_path = os.path.join(RESOURCE_ROOT, input_path)

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    page = reader.pages[0]
    writer.insert_page(page, 0)
    writer.remove_text(ignore_byte_string_object=ignoreByteStringObject)

    # finally, write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_writer_removed_text.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_write_metadata():
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    metadata = reader.metadata
    writer.add_metadata(metadata)

    writer.add_metadata({"/Title": "The Crazy Ones"})

    # finally, write data to PyPDF2-output.pdf
    tmp_filename = "dont_commit_writer_added_metadata.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Check if the title was set
    reader = PdfReader(tmp_filename)
    metadata = reader.metadata
    assert metadata.get("/Title") == "The Crazy Ones"

    # Cleanup
    os.remove(tmp_filename)


def test_fill_form():
    reader = PdfReader(os.path.join(RESOURCE_ROOT, "form.pdf"))
    writer = PdfWriter()

    page = reader.pages[0]

    writer.add_page(page)

    writer.update_page_form_field_values(
        writer.get_page(0), {"foo": "some filled in text"}, flags=1
    )

    # write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_filled_pdf.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)


def test_encrypt():
    reader = PdfReader(os.path.join(RESOURCE_ROOT, "form.pdf"))
    writer = PdfWriter()

    page = reader.pages[0]

    writer.add_page(page)
    writer.encrypt(user_pwd="userpwd", owner_pwd="ownerpwd", use_128bit=False)

    # write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_encrypted.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_add_bookmark():
    reader = PdfReader(os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf"))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    bookmark = writer.add_bookmark(
        "A bookmark", 1, None, (255, 0, 15), True, True, "/Fit", 200, 0, None
    )
    writer.add_bookmark("Another", 2, bookmark, None, False, False, "/Fit", 0, 0, None)

    # write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_bookmark.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_add_named_destination():
    reader = PdfReader(os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf"))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    from PyPDF2.generic import NameObject

    writer.add_named_destination(NameObject("A named dest"), 2)
    writer.add_named_destination(NameObject("A named dest2"), 2)

    from PyPDF2.generic import IndirectObject

    assert writer.get_named_dest_root() == [
        "A named dest",
        IndirectObject(7, 0, writer),
        "A named dest2",
        IndirectObject(10, 0, writer),
    ]

    # write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_named_destination.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_add_uri():
    reader = PdfReader(os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf"))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    from PyPDF2.generic import RectangleObject

    writer.add_uri(
        1,
        "http://www.example.com",
        RectangleObject([0, 0, 100, 100]),
        border=[1, 2, 3, [4]],
    )
    writer.add_uri(
        2,
        "https://pypdf2.readthedocs.io/en/latest/",
        RectangleObject([20, 30, 50, 80]),
        border=[1, 2, 3],
    )
    writer.add_uri(
        3,
        "https://pypdf2.readthedocs.io/en/latest/user/adding-pdf-annotations.html",
        "[ 200 300 250 350 ]",
        border=[0, 0, 0],
    )
    writer.add_uri(
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
    reader = PdfReader(os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf"))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    from PyPDF2.generic import RectangleObject

    writer.add_link(
        1,
        2,
        RectangleObject([0, 0, 100, 100]),
        border=[1, 2, 3, [4]],
        fit="/Fit",
    )
    writer.add_link(2, 3, RectangleObject([20, 30, 50, 80]), [1, 2, 3], "/FitH", None)
    writer.add_link(
        3,
        0,
        "[ 200 300 250 350 ]",
        [0, 0, 0],
        "/XYZ",
        0,
        0,
        2,
    )
    writer.add_link(
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
    reader = PdfReader(bytes_stream)
    assert reader.numPages == 4

    # Write to bytes stream
    writer = PdfWriter()
    with BytesIO() as output_stream:
        writer.write(output_stream)


def test_regression_issue670():
    filepath = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    reader = PdfReader(filepath, strict=False, overwriteWarnings=False)
    for _ in range(2):
        pdf_writer = PdfWriter()
        pdf_writer.add_page(reader._get_page(0))
        with open("dont_commit_issue670.pdf", "wb") as f_pdf:
            pdf_writer.write(f_pdf)
