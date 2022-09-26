import os
from io import BytesIO
from pathlib import Path

import pytest

from PyPDF2 import PageObject, PdfMerger, PdfReader, PdfWriter
from PyPDF2.errors import PageSizeNotDefinedError
from PyPDF2.generic import (
    IndirectObject,
    NameObject,
    RectangleObject,
    StreamObject,
    TextStringObject,
)

from . import get_pdf_from_url

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
EXTERNAL_ROOT = Path(PROJECT_ROOT) / "sample-files"


def test_writer_exception_non_binary(tmp_path, caplog):
    src = RESOURCE_ROOT / "pdflatex-outline.pdf"

    reader = PdfReader(src)
    writer = PdfWriter()
    writer.add_page(reader.pages[0])

    with open(tmp_path / "out.txt", "w") as fp:
        with pytest.raises(TypeError):
            writer.write_stream(fp)
    ending = "to write to is not in binary mode. It may not be written to correctly.\n"
    assert caplog.text.endswith(ending)


def test_writer_clone():
    src = RESOURCE_ROOT / "pdflatex-outline.pdf"

    reader = PdfReader(src)
    writer = PdfWriter()

    writer.clone_document_from_reader(reader)
    assert len(writer.pages) == 4


def writer_operate(writer):
    """
    To test the writer that initialized by each of the four usages.
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
        "An outline item", 0, None, (255, 0, 15), True, True, "/FitBV", 10
    )
    writer.add_outline_item(
        "The XYZ fit", 0, oi, (255, 0, 15), True, True, "/XYZ", 10, 20, 3
    )
    writer.add_outline_item(
        "The FitH fit", 0, oi, (255, 0, 15), True, True, "/FitH", 10
    )
    writer.add_outline_item(
        "The FitV fit", 0, oi, (255, 0, 15), True, True, "/FitV", 10
    )
    writer.add_outline_item(
        "The FitR fit", 0, oi, (255, 0, 15), True, True, "/FitR", 10, 20, 30, 40
    )
    writer.add_outline_item("The FitB fit", 0, oi, (255, 0, 15), True, True, "/FitB")
    writer.add_outline_item(
        "The FitBH fit", 0, oi, (255, 0, 15), True, True, "/FitBH", 10
    )
    writer.add_outline_item(
        "The FitBV fit", 0, oi, (255, 0, 15), True, True, "/FitBV", 10
    )
    writer.add_blank_page()
    writer.add_uri(2, "https://example.com", RectangleObject([0, 0, 100, 100]))
    with pytest.warns(PendingDeprecationWarning):
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

    # TODO: This gives "KeyError: '/Contents'" - is that a bug?
    # writer.removeImages()

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

    # finally, write "output" to PyPDF2-output.pdf
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

        # finally, write "output" to PyPDF2-output.pdf
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

        # finally, write "output" to PyPDF2-output.pdf
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
    # This includes write "output" to PyPDF2-output.pdf
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

    # finally, write "output" to PyPDF2-output.pdf
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

    # finally, write "output" to PyPDF2-output.pdf
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
        # startx_correction should be -1 due to double % at the beginning inducing an error on startxref computation
        pdf_data.find(b"xref"),
    )
    print(pdf_data.decode())
    pdf_stream = BytesIO(pdf_data)

    reader = PdfReader(pdf_stream, strict=False)
    writer = PdfWriter()

    page = reader.pages[0]
    writer.insert_page(page, 0)
    writer.remove_text(ignore_byte_string_object=ignore_byte_string_object)

    # finally, write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_writer_removed_text.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    # Cleanup
    os.remove(tmp_filename)


def test_write_metadata():
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"

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

    # write "output" to PyPDF2-output.pdf
    tmp_filename = "dont_commit_filled_pdf.pdf"
    with open(tmp_filename, "wb") as output_stream:
        writer.write(output_stream)

    os.remove(tmp_filename)  # cleanup


@pytest.mark.parametrize(
    ("use_128bit", "user_pwd", "owner_pwd"),
    [(True, "userpwd", "ownerpwd"), (False, "userpwd", "ownerpwd")],
)
def test_encrypt(use_128bit, user_pwd, owner_pwd):
    reader = PdfReader(RESOURCE_ROOT / "form.pdf")
    writer = PdfWriter()

    page = reader.pages[0]
    orig_text = page.extract_text()

    writer.add_page(page)
    writer.encrypt(user_pwd=user_pwd, owner_pwd=owner_pwd, use_128bit=use_128bit)

    # write "output" to PyPDF2-output.pdf
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
    assert reader.metadata.get("/Producer") == "PyPDF2"
    assert new_text == orig_text

    # Test the owner password (str):
    reader = PdfReader(tmp_filename, password="ownerpwd")
    new_text = reader.pages[0].extract_text()
    assert reader.metadata.get("/Producer") == "PyPDF2"
    assert new_text == orig_text

    # Test the user password (bytes):
    reader = PdfReader(tmp_filename, password=b"userpwd")
    new_text = reader.pages[0].extract_text()
    assert reader.metadata.get("/Producer") == "PyPDF2"
    assert new_text == orig_text

    # Test the owner password (stbytesr):
    reader = PdfReader(tmp_filename, password=b"ownerpwd")
    new_text = reader.pages[0].extract_text()
    assert reader.metadata.get("/Producer") == "PyPDF2"
    assert new_text == orig_text

    # Cleanup
    os.remove(tmp_filename)


def test_add_outline_item():
    reader = PdfReader(RESOURCE_ROOT / "pdflatex-outline.pdf")
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    outline_item = writer.add_outline_item(
        "An outline item", 1, None, (255, 0, 15), True, True, "/Fit", 200, 0, None
    )
    writer.add_outline_item(
        "Another", 2, outline_item, None, False, False, "/Fit", 0, 0, None
    )

    # write "output" to PyPDF2-output.pdf
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
    assert root[1].get_object()["/D"][0] == writer.pages[2].indirect_ref
    assert root[2] == "A named dest2"
    assert root[3].pdf == writer
    assert root[3].get_object()["/S"] == NameObject("/GoTo")
    assert root[3].get_object()["/D"][0] == writer.pages[2].indirect_ref

    # write "output" to PyPDF2-output.pdf
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
    reader = PdfReader(RESOURCE_ROOT / "pdflatex-outline.pdf")
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    with pytest.warns(
        PendingDeprecationWarning,
        match="add_link is deprecated and will be removed in PyPDF2",
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

    # write "output" to PyPDF2-output.pdf
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
    """
    Test with invalid stream length object
    """
    with open(RESOURCE_ROOT / "issue-301.pdf", "rb") as f:
        reader = PdfReader(f)
        writer = PdfWriter()
        writer.append_pages_from_reader(reader)
        o = BytesIO()
        writer.write(o)


def test_append_pages_from_reader_append():
    """use append_pages_from_reader with a callable"""
    with open(RESOURCE_ROOT / "issue-301.pdf", "rb") as f:
        reader = PdfReader(f)
        writer = PdfWriter()
        writer.append_pages_from_reader(reader, callable)
        o = BytesIO()
        writer.write(o)


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
    os.remove(target)  # remove for testing


def test_deprecate_bookmark_decorator():
    reader = PdfReader(RESOURCE_ROOT / "outlines-with-invalid-destinations.pdf")
    page = reader.pages[0]
    outline_item = reader.outline[0]
    writer = PdfWriter()
    writer.add_page(page)
    with pytest.warns(
        UserWarning,
        match="bookmark is deprecated as an argument. Use outline_item instead",
    ):
        writer.add_outline_item_dict(bookmark=outline_item)


def test_colors_in_outline_item():
    reader = PdfReader(EXTERNAL_ROOT / "004-pdflatex-4-pages/pdflatex-4-pages.pdf")
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    purple_rgb = (0.50196, 0, 0.50196)
    writer.add_outline_item("First Outline Item", pagenum=2, color="800080")
    writer.add_outline_item("Second Outline Item", pagenum=3, color="#800080")
    writer.add_outline_item("Third Outline Item", pagenum=4, color=purple_rgb)

    target = "tmp-named-color-outline.pdf"
    with open(target, "wb") as f:
        writer.write(f)

    reader2 = PdfReader(target)
    for outline_item in reader2.outline:
        # convert float to string because of mutability
        assert [str(c) for c in outline_item.color] == [str(p) for p in purple_rgb]

    # Cleanup
    os.remove(target)  # remove for testing


def test_write_empty_stream():
    reader = PdfReader(EXTERNAL_ROOT / "004-pdflatex-4-pages/pdflatex-4-pages.pdf")
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    with pytest.raises(ValueError) as exc:
        writer.write("")
    assert exc.value.args[0] == "Output(stream=) is empty."
