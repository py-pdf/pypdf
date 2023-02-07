import os
import re
from io import BytesIO
from pathlib import Path

import pytest

from pypdf import PageObject, PdfMerger, PdfReader, PdfWriter, Transformation
from pypdf.errors import DeprecationError, PageSizeNotDefinedError
from pypdf.generic import (
    ArrayObject,
    ContentStream,
    Fit,
    IndirectObject,
    NameObject,
    NumberObject,
    RectangleObject,
    StreamObject,
    TextStringObject,
)

from . import get_pdf_from_url

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
SAMPLE_ROOT = Path(PROJECT_ROOT) / "sample-files"


def test_writer_exception_non_binary(tmp_path, caplog):
    src = RESOURCE_ROOT / "pdflatex-outline.pdf"

    reader = PdfReader(src)
    writer = PdfWriter()
    writer.add_page(reader.pages[0])

    with open(tmp_path / "out.txt", "w") as fp, pytest.raises(TypeError):
        writer.write_stream(fp)
    ending = "to write to is not in binary mode. It may not be written to correctly.\n"
    assert caplog.text.endswith(ending)


def test_writer_clone():
    src = RESOURCE_ROOT / "pdflatex-outline.pdf"

    reader = PdfReader(src)
    writer = PdfWriter()

    writer.clone_document_from_reader(reader)
    assert len(writer.pages) == 4


def test_writer_clone_bookmarks():
    # Arrange
    src = RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR-crazyones-merged.pdf"
    reader = PdfReader(src)
    writer = PdfWriter()

    # Act + test cat
    cat = ""

    def cat1(p):
        nonlocal cat
        cat += p.__repr__()

    writer.clone_document_from_reader(reader, cat1)
    assert "/Page" in cat
    assert writer.pages[0].raw_get("/Parent") == writer._pages
    writer.add_outline_item("Page 1", 0)
    writer.add_outline_item("Page 2", 1)

    # Assert
    bytes_stream = BytesIO()
    writer.write(bytes_stream)
    bytes_stream.seek(0)
    reader2 = PdfReader(bytes_stream)
    assert len(reader2.pages) == len(reader.pages)
    assert len(reader2.outline) == 2

    # test with append
    writer = PdfWriter()
    writer.append(reader)
    writer.add_outline_item("Page 1", 0)
    writer.add_outline_item("Page 2", 1)

    # Assert
    bytes_stream = BytesIO()
    writer.write(bytes_stream)
    bytes_stream.seek(0)
    reader2 = PdfReader(bytes_stream)
    assert len(reader2.pages) == len(reader.pages)
    assert len(reader2.outline) == 2


def writer_operate(writer: PdfWriter) -> None:
    """
    To test the writer that initialized by each of the four usages.

    Args:
        writer: A PdfWriter object
    """
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    pdf_outline_path = RESOURCE_ROOT / "pdflatex-outline.pdf"

    reader = PdfReader(pdf_path)
    reader_outline = PdfReader(pdf_outline_path)

    page = reader.pages[0]
    with pytest.raises(PageSizeNotDefinedError) as exc:
        writer.add_blank_page()
    assert exc.value.args == ()
    writer.insert_page(page, 1)
    writer.insert_page(reader_outline.pages[0], 0)
    writer.add_outline_item_destination(page)
    writer.remove_links()
    writer.add_outline_item_destination(page)
    oi = writer.add_outline_item(
        "An outline item", 0, None, (255, 0, 15), True, True, Fit.fit_box_vertically(10)
    )
    writer.add_outline_item(
        "The XYZ fit", 0, oi, (255, 0, 15), True, True, Fit.xyz(left=10, top=20, zoom=3)
    )
    writer.add_outline_item(
        "The FitH fit", 0, oi, (255, 0, 15), True, True, Fit.fit_horizontally(top=10)
    )
    writer.add_outline_item(
        "The FitV fit", 0, oi, (255, 0, 15), True, True, Fit.fit_vertically(left=10)
    )
    writer.add_outline_item(
        "The FitR fit",
        0,
        oi,
        (255, 0, 15),
        True,
        True,
        Fit.fit_rectangle(left=10, bottom=20, right=30, top=40),
    )
    writer.add_outline_item(
        "The FitB fit", 0, oi, (255, 0, 15), True, True, Fit.fit_box()
    )
    writer.add_outline_item(
        "The FitBH fit",
        0,
        oi,
        (255, 0, 15),
        True,
        True,
        Fit.fit_box_horizontally(top=10),
    )
    writer.add_outline_item(
        "The FitBV fit",
        0,
        oi,
        (255, 0, 15),
        True,
        True,
        Fit.fit_box_vertically(left=10),
    )
    writer.add_blank_page()
    writer.add_uri(2, "https://example.com", RectangleObject([0, 0, 100, 100]))
    with pytest.raises(DeprecationError):
        writer.add_link(2, 1, RectangleObject([0, 0, 100, 100]))
    assert writer._get_page_layout() is None
    writer.page_layout = "broken"
    assert writer.page_layout == "broken"
    writer.page_layout = NameObject("/SinglePage")
    assert writer._get_page_layout() == "/SinglePage"
    assert writer._get_page_mode() is None
    writer.set_page_mode("/UseNone")
    assert writer._get_page_mode() == "/UseNone"
    writer.insert_blank_page(width=100, height=100)
    writer.insert_blank_page()  # without parameters

    writer.remove_images()

    writer.add_metadata({"author": "Martin Thoma"})

    writer.add_attachment("foobar.gif", b"foobarcontent")

    # Check that every key in _idnum_hash is correct
    objects_hash = [o.hash_value() for o in writer._objects]
    for k, v in writer._idnum_hash.items():
        assert v.pdf == writer
        assert k in objects_hash, f"Missing {v}"


tmp_path = "dont_commit_writer.pdf"


@pytest.mark.parametrize(
    ("write_data_here", "needs_cleanup"),
    [
        ("dont_commit_writer.pdf", True),
        (Path("dont_commit_writer.pdf"), True),
        (BytesIO(), False),
    ],
)
def test_writer_operations_by_traditional_usage(write_data_here, needs_cleanup):
    writer = PdfWriter()

    writer_operate(writer)

    # finally, write "output" to pypdf-output.pdf
    if needs_cleanup:
        with open(write_data_here, "wb") as output_stream:
            writer.write(output_stream)
    else:
        output_stream = write_data_here
        writer.write(output_stream)

    if needs_cleanup:
        os.remove(write_data_here)


@pytest.mark.parametrize(
    ("write_data_here", "needs_cleanup"),
    [
        ("dont_commit_writer.pdf", True),
        (Path("dont_commit_writer.pdf"), True),
        (BytesIO(), False),
    ],
)
def test_writer_operations_by_semi_traditional_usage(write_data_here, needs_cleanup):
    with PdfWriter() as writer:
        writer_operate(writer)

        # finally, write "output" to pypdf-output.pdf
        if needs_cleanup:
            with open(write_data_here, "wb") as output_stream:
                writer.write(output_stream)
        else:
            output_stream = write_data_here
            writer.write(output_stream)

    if needs_cleanup:
        os.remove(write_data_here)


@pytest.mark.parametrize(
    ("write_data_here", "needs_cleanup"),
    [
        ("dont_commit_writer.pdf", True),
        (Path("dont_commit_writer.pdf"), True),
        (BytesIO(), False),
    ],
)
def test_writer_operations_by_semi_new_traditional_usage(
    write_data_here, needs_cleanup
):
    with PdfWriter() as writer:
        writer_operate(writer)

        # finally, write "output" to pypdf-output.pdf
        writer.write(write_data_here)

    if needs_cleanup:
        os.remove(write_data_here)


@pytest.mark.parametrize(
    ("write_data_here", "needs_cleanup"),
    [
        ("dont_commit_writer.pdf", True),
        (Path("dont_commit_writer.pdf"), True),
        (BytesIO(), False),
    ],
)
def test_writer_operation_by_new_usage(write_data_here, needs_cleanup):
    # This includes write "output" to pypdf-output.pdf
    with PdfWriter(write_data_here) as writer:
        writer_operate(writer)

    if needs_cleanup:
        os.remove(write_data_here)


@pytest.mark.parametrize(
    ("input_path", "ignore_byte_string_object"),
    [
        ("side-by-side-subfig.pdf", False),
        ("reportlab-inline-image.pdf", True),
    ],
)
def test_remove_images(input_path, ignore_byte_string_object):
    pdf_path = RESOURCE_ROOT / input_path

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    page = reader.pages[0]
    writer.insert_page(page, 0)
    writer.remove_images(ignore_byte_string_object=ignore_byte_string_object)

    # finally, write "output" to pypdf-output.pdf
    tmp_filename = "dont_commit_writer_removed_image.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    with open(tmp_filename, "rb") as input_stream:
        reader = PdfReader(input_stream)
        if input_path == "side-by-side-subfig.pdf":
            extracted_text = reader.pages[0].extract_text()
            assert "Lorem ipsum dolor sit amet" in extracted_text

    # Cleanup
    os.remove(tmp_filename)


@pytest.mark.parametrize(
    ("input_path", "ignore_byte_string_object"),
    [
        ("side-by-side-subfig.pdf", False),
        ("side-by-side-subfig.pdf", True),
        ("reportlab-inline-image.pdf", False),
        ("reportlab-inline-image.pdf", True),
    ],
)
def test_remove_text(input_path, ignore_byte_string_object):
    pdf_path = RESOURCE_ROOT / input_path

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    page = reader.pages[0]
    writer.insert_page(page, 0)
    writer.remove_text(ignore_byte_string_object=ignore_byte_string_object)

    # finally, write "output" to pypdf-output.pdf
    tmp_filename = "dont_commit_writer_removed_text.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


@pytest.mark.parametrize(
    ("ignore_byte_string_object"),
    [False, True],
)
def test_remove_text_all_operators(ignore_byte_string_object):
    stream = (
        b"BT "
        b"/F0 36 Tf "
        b"50 706 Td "
        b"36 TL "
        b"(The Tj operator) Tj "
        b'1 2 (The double quote operator) " '
        b"(The single quote operator) ' "
        b"ET"
    )
    pdf_data = (
        b"%%PDF-1.7\n"
        b"1 0 obj << /Count 1 /Kids [5 0 R] /Type /Pages >> endobj\n"
        b"2 0 obj << >> endobj\n"
        b"3 0 obj << >> endobj\n"
        b"4 0 obj << /Length %d >>\n"
        b"stream\n" + (b"%s\n" % stream) + b"endstream\n"
        b"endobj\n"
        b"5 0 obj << /Contents 4 0 R /CropBox [0.0 0.0 2550.0 3508.0]\n"
        b" /MediaBox [0.0 0.0 2550.0 3508.0] /Parent 1 0 R"
        b" /Resources << /Font << >> >>"
        b" /Rotate 0 /Type /Page >> endobj\n"
        b"6 0 obj << /Pages 1 0 R /Type /Catalog >> endobj\n"
        b"xref 1 6\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"trailer << /Root 6 0 R /Size 6 >>\n"
        b"startxref\n%d\n"
        b"%%%%EOF"
    )
    startx_correction = -1
    pdf_data = pdf_data % (
        len(stream),
        pdf_data.find(b"1 0 obj") + startx_correction,
        pdf_data.find(b"2 0 obj") + startx_correction,
        pdf_data.find(b"3 0 obj") + startx_correction,
        pdf_data.find(b"4 0 obj") + startx_correction,
        pdf_data.find(b"5 0 obj") + startx_correction,
        pdf_data.find(b"6 0 obj") + startx_correction,
        # startx_correction should be -1 due to double % at the beginning
        # inducing an error on startxref computation
        pdf_data.find(b"xref"),
    )
    print(pdf_data.decode())
    pdf_stream = BytesIO(pdf_data)

    reader = PdfReader(pdf_stream, strict=False)
    writer = PdfWriter()

    page = reader.pages[0]
    writer.insert_page(page, 0)
    writer.remove_text(ignore_byte_string_object=ignore_byte_string_object)

    # finally, write "output" to pypdf-output.pdf
    tmp_filename = "dont_commit_writer_removed_text.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_write_metadata():
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    writer.add_page(reader.pages[0])
    for page in reader.pages:
        writer.add_page(page)

    metadata = reader.metadata
    writer.add_metadata(metadata)

    writer.add_metadata({"/Title": "The Crazy Ones"})

    # finally, write data to pypdf-output.pdf
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
    reader = PdfReader(RESOURCE_ROOT / "form.pdf")
    writer = PdfWriter()

    page = reader.pages[0]

    writer.add_page(page)
    writer.add_page(PdfReader(RESOURCE_ROOT / "crazyones.pdf").pages[0])

    writer.update_page_form_field_values(
        writer.pages[0], {"foo": "some filled in text"}, flags=1
    )

    # check if no fields to fill in the page
    writer.update_page_form_field_values(
        writer.pages[1], {"foo": "some filled in text"}, flags=1
    )

    writer.update_page_form_field_values(
        writer.pages[0], {"foo": "some filled in text"}
    )

    # write "output" to pypdf-output.pdf
    tmp_filename = "dont_commit_filled_pdf.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    os.remove(tmp_filename)  # cleanup


@pytest.mark.parametrize(
    ("use_128bit", "user_password", "owner_password"),
    [(True, "userpwd", "ownerpwd"), (False, "userpwd", "ownerpwd")],
)
def test_encrypt(use_128bit, user_password, owner_password):
    reader = PdfReader(RESOURCE_ROOT / "form.pdf")
    writer = PdfWriter()

    page = reader.pages[0]
    orig_text = page.extract_text()

    writer.add_page(page)
    writer.encrypt(
        user_password=user_password,
        owner_password=owner_password,
        use_128bit=use_128bit,
    )

    # write "output" to pypdf-output.pdf
    tmp_filename = "dont_commit_encrypted.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Test that the data is not there in clear text
    with open(tmp_filename, "rb") as input_stream:
        data = input_stream.read()
    assert b"foo" not in data

    # Test the user password (str):
    reader = PdfReader(tmp_filename, password="userpwd")
    new_text = reader.pages[0].extract_text()
    assert reader.metadata.get("/Producer") == "pypdf"
    assert new_text == orig_text

    # Test the owner password (str):
    reader = PdfReader(tmp_filename, password="ownerpwd")
    new_text = reader.pages[0].extract_text()
    assert reader.metadata.get("/Producer") == "pypdf"
    assert new_text == orig_text

    # Test the user password (bytes):
    reader = PdfReader(tmp_filename, password=b"userpwd")
    new_text = reader.pages[0].extract_text()
    assert reader.metadata.get("/Producer") == "pypdf"
    assert new_text == orig_text

    # Test the owner password (stbytesr):
    reader = PdfReader(tmp_filename, password=b"ownerpwd")
    new_text = reader.pages[0].extract_text()
    assert reader.metadata.get("/Producer") == "pypdf"
    assert new_text == orig_text

    # Cleanup
    os.remove(tmp_filename)


def test_add_outline_item():
    reader = PdfReader(RESOURCE_ROOT / "pdflatex-outline.pdf")
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    outline_item = writer.add_outline_item(
        "An outline item", 1, None, (255, 0, 15), True, True, Fit.fit()
    )
    writer.add_outline_item("Another", 2, outline_item, None, False, False, Fit.fit())

    # write "output" to pypdf-output.pdf
    tmp_filename = "dont_commit_outline_item.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_add_named_destination():
    reader = PdfReader(RESOURCE_ROOT / "pdflatex-outline.pdf")
    writer = PdfWriter()
    assert writer.get_named_dest_root() == []

    for page in reader.pages:
        writer.add_page(page)

    assert writer.get_named_dest_root() == []

    writer.add_named_destination(TextStringObject("A named dest"), 2)
    writer.add_named_destination(TextStringObject("A named dest2"), 2)

    root = writer.get_named_dest_root()
    assert root[0] == "A named dest"
    assert root[1].pdf == writer
    assert root[1].get_object()["/S"] == NameObject("/GoTo")
    assert root[1].get_object()["/D"][0] == writer.pages[2].indirect_reference
    assert root[2] == "A named dest2"
    assert root[3].pdf == writer
    assert root[3].get_object()["/S"] == NameObject("/GoTo")
    assert root[3].get_object()["/D"][0] == writer.pages[2].indirect_reference

    # test get_object

    assert writer.get_object(root[1].idnum) == writer.get_object(root[1])
    with pytest.raises(ValueError) as exc:
        writer.get_object(reader.pages[0].indirect_reference)
    assert exc.value.args[0] == "pdf must be self"

    # write "output" to pypdf-output.pdf
    tmp_filename = "dont_commit_named_destination.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_add_uri():
    reader = PdfReader(RESOURCE_ROOT / "pdflatex-outline.pdf")
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.add_uri(
        1,
        "http://www.example.com",
        RectangleObject([0, 0, 100, 100]),
        border=[1, 2, 3, [4]],
    )
    writer.add_uri(
        2,
        "https://pypdf.readthedocs.io/en/latest/",
        RectangleObject([20, 30, 50, 80]),
        border=[1, 2, 3],
    )
    writer.add_uri(
        3,
        "https://pypdf.readthedocs.io/en/latest/user/adding-pdf-annotations.html",
        "[ 200 300 250 350 ]",
        border=[0, 0, 0],
    )
    writer.add_uri(
        3,
        "https://pypdf.readthedocs.io/en/latest/user/adding-pdf-annotations.html",
        [100, 200, 150, 250],
        border=[0, 0, 0],
    )

    # write "output" to pypdf-output.pdf
    tmp_filename = "dont_commit_uri.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_add_link():
    reader = PdfReader(RESOURCE_ROOT / "pdflatex-outline.pdf")
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    with pytest.raises(
        DeprecationError,
        match=(
            re.escape(
                "add_link is deprecated and was removed in pypdf 3.0.0. "
                "Use add_annotation(AnnotationBuilder.link(...)) instead."
            )
        ),
    ):
        writer.add_link(
            1,
            2,
            RectangleObject([0, 0, 100, 100]),
            border=[1, 2, 3, [4]],
            fit="/Fit",
        )
        writer.add_link(
            2, 3, RectangleObject([20, 30, 50, 80]), [1, 2, 3], "/FitH", None
        )
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

    # write "output" to pypdf-output.pdf
    tmp_filename = "dont_commit_link.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_io_streams():
    """This is the example from the docs ("Streaming data")."""
    filepath = RESOURCE_ROOT / "pdflatex-outline.pdf"
    with open(filepath, "rb") as fh:
        bytes_stream = BytesIO(fh.read())

    # Read from bytes stream
    reader = PdfReader(bytes_stream)
    assert len(reader.pages) == 4

    # Write to bytes stream
    writer = PdfWriter()
    with BytesIO() as output_stream:
        writer.write(output_stream)


def test_regression_issue670():
    tmp_file = "dont_commit_issue670.pdf"
    filepath = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(filepath, strict=False)
    for _ in range(2):
        writer = PdfWriter()
        writer.add_page(reader.pages[0])
        with open(tmp_file, "wb") as f_pdf:
            writer.write(f_pdf)

    # cleanup
    os.remove(tmp_file)


def test_issue301():
    """Test with invalid stream length object."""
    with open(RESOURCE_ROOT / "issue-301.pdf", "rb") as f:
        reader = PdfReader(f)
        writer = PdfWriter()
        writer.append_pages_from_reader(reader)
        o = BytesIO()
        writer.write(o)


def test_append_pages_from_reader_append():
    """Use append_pages_from_reader with a callable."""
    with open(RESOURCE_ROOT / "issue-301.pdf", "rb") as f:
        reader = PdfReader(f)
        writer = PdfWriter()
        writer.append_pages_from_reader(reader, callable)
        o = BytesIO()
        writer.write(o)


@pytest.mark.external
@pytest.mark.slow
def test_sweep_indirect_references_nullobject_exception():
    # TODO: Check this more closely... this looks weird
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/924/924666.pdf"
    name = "tika-924666.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfMerger()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
@pytest.mark.slow
def test_write_outline_item_on_page_fitv():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/922/922840.pdf"
    name = "tika-922840.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfMerger()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


def test_pdf_header():
    writer = PdfWriter()
    assert writer.pdf_header == b"%PDF-1.3"

    reader = PdfReader(RESOURCE_ROOT / "crazyones.pdf")
    writer.add_page(reader.pages[0])
    assert writer.pdf_header == b"%PDF-1.5"

    writer.pdf_header = b"%PDF-1.6"
    assert writer.pdf_header == b"%PDF-1.6"


def test_write_dict_stream_object():
    stream = (
        b"BT "
        b"/F0 36 Tf "
        b"50 706 Td "
        b"36 TL "
        b"(The Tj operator) Tj "
        b'1 2 (The double quote operator) " '
        b"(The single quote operator) ' "
        b"ET"
    )

    stream_object = StreamObject()
    stream_object[NameObject("/Type")] = NameObject("/Text")
    stream_object._data = stream

    writer = PdfWriter()

    page_object = PageObject.create_blank_page(writer, 1000, 1000)
    # Construct dictionary object (PageObject) with stream object
    # Writer will replace this stream object with indirect object
    page_object[NameObject("/Test")] = stream_object

    page_object = writer.add_page(page_object)

    with open("tmp-writer-do-not-commit.pdf", "wb") as fp:
        writer.write(fp)

    for k, v in page_object.items():
        if k == "/Test":
            assert str(v) != str(stream_object)
            assert isinstance(v, IndirectObject)
            assert str(v.get_object()) == str(stream_object)
            break
    else:
        assert False, "/Test not found"

    # Check that every key in _idnum_hash is correct
    objects_hash = [o.hash_value() for o in writer._objects]
    for k, v in writer._idnum_hash.items():
        assert v.pdf == writer
        assert k in objects_hash, "Missing %s" % v

    os.remove("tmp-writer-do-not-commit.pdf")


def test_add_single_annotation():
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)

    annot_dict = {
        "/Type": "/Annot",
        "/Subtype": "/Text",
        "/Rect": [270.75, 596.25, 294.75, 620.25],
        "/Contents": "Note in second paragraph",
        "/C": [1, 1, 0],
        "/M": "D:20220406191858+02'00",
        "/Popup": {
            "/Type": "/Annot",
            "/Subtype": "/Popup",
            "/Rect": [294.75, 446.25, 494.75, 596.25],
            "/M": "D:20220406191847+02'00",
        },
        "/T": "moose",
    }
    writer.add_annotation(0, annot_dict)
    # Assert manually
    target = "annot-single-out.pdf"
    with open(target, "wb") as fp:
        writer.write(fp)

    # Cleanup
    os.remove(target)  # comment out for testing


def test_deprecation_bookmark_decorator():
    reader = PdfReader(RESOURCE_ROOT / "outlines-with-invalid-destinations.pdf")
    page = reader.pages[0]
    outline_item = reader.outline[0]
    writer = PdfWriter()
    writer.add_page(page)
    with pytest.raises(
        DeprecationError,
        match="bookmark is deprecated as an argument. Use outline_item instead",
    ):
        writer.add_outline_item_dict(bookmark=outline_item)


@pytest.mark.samples
def test_colors_in_outline_item():
    reader = PdfReader(SAMPLE_ROOT / "004-pdflatex-4-pages/pdflatex-4-pages.pdf")
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    purple_rgb = (0.5019607843137255, 0.0, 0.5019607843137255)
    writer.add_outline_item("First Outline Item", page_number=2, color="800080")
    writer.add_outline_item("Second Outline Item", page_number=3, color="#800080")
    writer.add_outline_item("Third Outline Item", page_number=4, color=purple_rgb)

    target = "tmp-named-color-outline.pdf"
    with open(target, "wb") as f:
        writer.write(f)

    reader2 = PdfReader(target)
    for outline_item in reader2.outline:
        # convert float to string because of mutability
        assert [str(c) for c in outline_item.color] == [str(p) for p in purple_rgb]

    # Cleanup
    os.remove(target)  # comment out for testing


@pytest.mark.samples
def test_write_empty_stream():
    reader = PdfReader(SAMPLE_ROOT / "004-pdflatex-4-pages/pdflatex-4-pages.pdf")
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    with pytest.raises(ValueError) as exc:
        writer.write("")
    assert exc.value.args[0] == "Output(stream=) is empty."


def test_startup_dest():
    pdf_file_writer = PdfWriter()
    pdf_file_writer.append_pages_from_reader(PdfReader(RESOURCE_ROOT / "issue-604.pdf"))

    assert pdf_file_writer.open_destination is None
    pdf_file_writer.open_destination = pdf_file_writer.pages[9]
    # checked also using Acrobrat to verify the good page is opened
    op = pdf_file_writer._root_object["/OpenAction"]
    assert op[0] == pdf_file_writer.pages[9].indirect_reference
    assert op[1] == "/Fit"
    op = pdf_file_writer.open_destination
    assert op.raw_get("/Page") == pdf_file_writer.pages[9].indirect_reference
    assert op["/Type"] == "/Fit"
    pdf_file_writer.open_destination = op
    assert pdf_file_writer.open_destination == op

    # irrelevant, just for coverage
    pdf_file_writer._root_object[NameObject("/OpenAction")][0] = NumberObject(0)
    pdf_file_writer.open_destination
    with pytest.raises(Exception) as exc:
        del pdf_file_writer._root_object[NameObject("/OpenAction")][0]
        pdf_file_writer.open_destination
    assert "Invalid Destination" in str(exc.value)

    pdf_file_writer.open_destination = "Test"
    # checked also using Acrobrat to verify open_destination
    op = pdf_file_writer._root_object["/OpenAction"]
    assert isinstance(op, TextStringObject)
    assert op == "Test"
    op = pdf_file_writer.open_destination
    assert isinstance(op, TextStringObject)
    assert op == "Test"

    # irrelevant, this is just for coverage
    pdf_file_writer._root_object[NameObject("/OpenAction")] = NumberObject(0)
    assert pdf_file_writer.open_destination is None
    pdf_file_writer.open_destination = None
    assert "/OpenAction" not in pdf_file_writer._root_object
    pdf_file_writer.open_destination = None


@pytest.mark.external
def test_iss471():
    url = "https://github.com/py-pdf/pypdf/files/9139245/book.pdf"
    name = "book_471.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))

    writer = PdfWriter()
    writer.append(reader, excluded_fields=[])
    assert isinstance(
        writer.pages[0]["/Annots"][0].get_object()["/Dest"], TextStringObject
    )


@pytest.mark.external
def test_reset_translation():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/924/924666.pdf"
    name = "tika-924666.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    writer = PdfWriter()
    writer.append(reader, (0, 10))
    nb = len(writer._objects)
    writer.append(reader, (0, 10))
    assert (
        len(writer._objects) == nb + 11
    )  # +10 (pages) +1 because of the added outline
    nb += 1
    writer.reset_translation(reader)
    writer.append(reader, (0, 10))
    assert len(writer._objects) >= nb + 200
    nb = len(writer._objects)
    writer.reset_translation(reader.pages[0].indirect_reference)
    writer.append(reader, (0, 10))
    assert len(writer._objects) >= nb + 200
    nb = len(writer._objects)
    writer.reset_translation()
    writer.append(reader, (0, 10))
    assert len(writer._objects) >= nb + 200
    nb = len(writer._objects)


def test_threads_empty():
    writer = PdfWriter()
    thr = writer.threads
    assert isinstance(thr, ArrayObject)
    assert len(thr) == 0
    thr2 = writer.threads
    assert thr == thr2


@pytest.mark.external
def test_append_without_annots_and_articles():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/924/924666.pdf"
    name = "tika-924666.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    writer = PdfWriter()
    writer.append(reader, None, (0, 10), True, ["/B"])
    writer.reset_translation()
    writer.append(reader, (0, 10), True, ["/B"])
    assert writer.threads == []
    writer = PdfWriter()
    writer.append(reader, None, (0, 10), True, ["/Annots"])
    assert "/Annots" not in writer.pages[5]
    writer = PdfWriter()
    writer.append(reader, None, (0, 10), True, [])
    assert "/Annots" in writer.pages[5]
    assert len(writer.threads) >= 1


@pytest.mark.external
def test_append_multiple():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/924/924666.pdf"
    name = "tika-924666.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    writer = PdfWriter()
    writer.append(
        reader, [0, 0, 0]
    )  # to demonstre multiple insertion of same page at once
    writer.append(reader, [0, 0, 0])  # second pack
    pages = writer._root_object["/Pages"]["/Kids"]
    assert pages[0] not in pages[1:]  # page not repeated
    assert pages[-1] not in pages[0:-1]  # page not repeated


@pytest.mark.samples
def test_set_page_label():
    src = RESOURCE_ROOT / "GeoBase_NHNC1_Data_Model_UML_EN.pdf"  # File without labels
    target = "pypdf-output.pdf"
    reader = PdfReader(src)

    expected = [
        "i",
        "ii",
        "1",
        "2",
        "A",
        "B",
        "1",
        "2",
        "3",
        "4",
        "A",
        "i",
        "I",
        "II",
        "1",
        "2",
        "3",
        "I",
        "II",
    ]

    # Tests full lenght with labels assigned at first and last elements
    # Tests different labels assigned to consecutive ranges
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.set_page_label(0, 1, "/r")
    writer.set_page_label(4, 5, "/A")
    writer.set_page_label(10, 10, "/A")
    writer.set_page_label(11, 11, "/r")
    writer.set_page_label(12, 13, "/R")
    writer.set_page_label(17, 18, "/R")
    writer.write(target)
    assert PdfReader(target).page_labels == expected

    writer = PdfWriter()  # Same labels, different set order
    writer.clone_document_from_reader(reader)
    writer.set_page_label(17, 18, "/R")
    writer.set_page_label(4, 5, "/A")
    writer.set_page_label(10, 10, "/A")
    writer.set_page_label(0, 1, "/r")
    writer.set_page_label(12, 13, "/R")
    writer.set_page_label(11, 11, "/r")
    writer.write(target)
    assert PdfReader(target).page_labels == expected

    # Tests labels assigned only in the middle
    # Tests label assigned to a range already containing labled ranges
    expected = ["1", "2", "i", "ii", "iii", "iv", "v", "1"]
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.set_page_label(3, 4, "/a")
    writer.set_page_label(5, 5, "/A")
    writer.set_page_label(2, 6, "/r")
    writer.write(target)
    assert PdfReader(target).page_labels[: len(expected)] == expected

    # Tests labels assigned inside a previously existing range
    expected = ["1", "2", "i", "a", "b", "A", "1", "1", "2"]
    # Ones repeat because user didnt cover the entire original range
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.set_page_label(2, 6, "/r")
    writer.set_page_label(3, 4, "/a")
    writer.set_page_label(5, 5, "/A")
    writer.write(target)
    assert PdfReader(target).page_labels[: len(expected)] == expected

    # Tests invalid user input
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    with pytest.raises(
        ValueError, match="at least one between style and prefix must be given"
    ):
        writer.set_page_label(0, 5, start=2)
    with pytest.raises(
        ValueError, match="page_index_from must be equal or greater then 0"
    ):
        writer.set_page_label(-1, 5, "/r")
    with pytest.raises(
        ValueError, match="page_index_to must be equal or greater then page_index_from"
    ):
        writer.set_page_label(5, 0, "/r")
    with pytest.raises(ValueError, match="page_index_to exceeds number of pages"):
        writer.set_page_label(0, 19, "/r")
    with pytest.raises(
        ValueError, match="if given, start must be equal or greater than one"
    ):
        writer.set_page_label(0, 5, "/r", start=-1)

    os.remove(target)

    src = (
        SAMPLE_ROOT / "009-pdflatex-geotopo/GeoTopo.pdf"
    )  # File with pre existing labels
    target = "pypdf-output.pdf"
    reader = PdfReader(src)

    # Tests adding labels to existing ones
    expected = ["i", "ii", "A", "B", "1"]
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.set_page_label(2, 3, "/A")
    writer.write(target)
    assert PdfReader(target).page_labels[: len(expected)] == expected

    # Tests replacing existing lables
    expected = ["A", "B", "1", "1", "2"]
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.set_page_label(0, 1, "/A")
    writer.write(target)
    assert PdfReader(target).page_labels[: len(expected)] == expected

    os.remove(target)

    # Tests prefix and start.
    src = RESOURCE_ROOT / "issue-604.pdf"  # File without page labels
    target = "page_labels_test.pdf"
    reader = PdfReader(src)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    writer.set_page_label(0, 0, prefix="FRONT")
    writer.set_page_label(1, 2, "/D", start=2)
    writer.set_page_label(3, 6, prefix="UPDATES")
    writer.set_page_label(7, 10, "/D", prefix="THYR-")
    writer.set_page_label(11, 21, "/D", prefix="PAP-")
    writer.set_page_label(22, 30, "/D", prefix="FOLL-")
    writer.set_page_label(31, 39, "/D", prefix="HURT-")
    writer.write(target)

    os.remove(target)  # comment to see result


def test_iss1601():
    url = "https://github.com/py-pdf/pypdf/files/10579503/badges-38.pdf"
    name = "badge-38.pdf"
    in_pdf = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    out_pdf = PdfWriter()
    page_1 = out_pdf.add_blank_page(
        in_pdf.pages[0].mediabox[2], in_pdf.pages[0].mediabox[3]
    )
    page_1.merge_transformed_page(in_pdf.pages[0], Transformation())
    assert (
        ContentStream(in_pdf.pages[0].get_contents(), in_pdf).get_data()
        in page_1.get_contents().get_data()
    )
    page_1 = out_pdf.add_blank_page(
        in_pdf.pages[0].mediabox[2], in_pdf.pages[0].mediabox[3]
    )
    page_1.merge_page(in_pdf.pages[0])
    assert (
        ContentStream(in_pdf.pages[0].get_contents(), in_pdf).get_data()
        in page_1.get_contents().get_data()
    )


def test_attachments():
    writer = PdfWriter()
    writer.add_blank_page(100, 100)
    b = BytesIO()
    writer.write(b)
    b.seek(0)
    reader = PdfReader(b)
    b = None
    assert reader.list_attachments() == []
    assert reader.get_attachments() == {}
    writer.add_attachment("foobar.txt", b"foobarcontent")
    writer.add_attachment("foobar2.txt", b"foobarcontent2")

    b = BytesIO()
    writer.write(b)
    b.seek(0)
    reader = PdfReader(b)
    b = None
    assert reader.list_attachments() == ["foobar.txt", "foobar2.txt"]
    att = reader.get_attachments()
    assert len(att) == 2
    assert att["foobar.txt"] == b"foobarcontent"
    att = reader.get_attachments("foobar2.txt")
    assert len(att) == 1
    assert att["foobar2.txt"] == b"foobarcontent2"
