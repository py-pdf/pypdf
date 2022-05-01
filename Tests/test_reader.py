import io
import os
import time
from sys import version_info

import pytest

from PyPDF2 import PdfFileReader
from PyPDF2.constants import ImageAttributes as IA
from PyPDF2.constants import PageAttributes as PG
from PyPDF2.constants import Ressources as RES
from PyPDF2.errors import PdfReadError
from PyPDF2.filters import _xobj_to_image

if version_info < (3, 0):
    from cStringIO import StringIO

    StreamIO = StringIO
else:
    from io import BytesIO

    StreamIO = BytesIO

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


@pytest.mark.parametrize(
    ("src", "num_pages"),
    [("selenium-PyPDF2-issue-177.pdf", 1), ("pdflatex-outline.pdf", 4)],
)
def test_get_num_pages(src, num_pages):
    src = os.path.join(RESOURCE_ROOT, src)
    reader = PdfFileReader(src)
    assert reader.numPages == num_pages


@pytest.mark.parametrize(
    ("pdf_path", "expected"),
    [
        (
            os.path.join(RESOURCE_ROOT, "crazyones.pdf"),
            {
                "/CreationDate": "D:20150604133406-06'00'",
                "/Creator": " XeTeX output 2015.06.04:1334",
                "/Producer": "xdvipdfmx (20140317)",
            },
        ),
        (
            os.path.join(RESOURCE_ROOT, "metadata.pdf"),
            {
                "/CreationDate": "D:20220415093243+02'00'",
                "/ModDate": "D:20220415093243+02'00'",
                "/Creator": "pdflatex, or other tool",
                "/Producer": "Latex with hyperref, or other system",
                "/Author": "Martin Thoma",
                "/Keywords": "Some Keywords, other keywords; more keywords",
                "/Subject": "The Subject",
                "/Title": "The Title",
                "/Trapped": "/False",
                "/PTEX.Fullbanner": (
                    "This is pdfTeX, Version "
                    "3.141592653-2.6-1.40.23 (TeX Live 2021) "
                    "kpathsea version 6.3.3"
                ),
            },
        ),
    ],
    ids=["crazyones", "metadata"],
)
def test_read_metadata(pdf_path, expected):
    with open(pdf_path, "rb") as inputfile:
        reader = PdfFileReader(inputfile)
        docinfo = reader.documentInfo
        metadict = dict(docinfo)
        assert metadict == expected
        docinfo.title
        docinfo.title_raw
        docinfo.author
        docinfo.author_raw
        docinfo.creator
        docinfo.creator_raw
        docinfo.producer
        docinfo.producer_raw
        docinfo.subject
        docinfo.subject_raw
        if "/Title" in metadict:
            assert metadict["/Title"] == docinfo.title


@pytest.mark.parametrize(
    "src",
    [
        (os.path.join(RESOURCE_ROOT, "crazyones.pdf")),
        (os.path.join(RESOURCE_ROOT, "commented.pdf")),
    ],
)
def test_get_annotations(src):
    reader = PdfFileReader(src)

    for page in reader.pages:
        if PG.ANNOTS in page:
            for annot in page[PG.ANNOTS]:
                subtype = annot.getObject()[IA.SUBTYPE]
                if subtype == "/Text":
                    annot.getObject()[PG.CONTENTS]


@pytest.mark.parametrize(
    "src",
    [
        (os.path.join(RESOURCE_ROOT, "attachment.pdf")),
        (os.path.join(RESOURCE_ROOT, "crazyones.pdf")),
    ],
)
def test_get_attachments(src):
    reader = PdfFileReader(src)

    attachments = {}
    for i in range(reader.numPages):
        page = reader.getPage(i)
        if PG.ANNOTS in page:
            for annotation in page[PG.ANNOTS]:
                annotobj = annotation.getObject()
                if annotobj[IA.SUBTYPE] == "/FileAttachment":
                    fileobj = annotobj["/FS"]
                    attachments[fileobj["/F"]] = fileobj["/EF"]["/F"].getData()
    return attachments


@pytest.mark.parametrize(
    ("src", "outline_elements"),
    [
        (os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf"), 9),
        (os.path.join(RESOURCE_ROOT, "crazyones.pdf"), 0),
    ],
)
def test_get_outlines(src, outline_elements):
    reader = PdfFileReader(src)
    outlines = reader.getOutlines()
    assert len(outlines) == outline_elements


@pytest.mark.parametrize(
    ("src", "nb_images"),
    [
        ("pdflatex-outline.pdf", 0),
        ("crazyones.pdf", 0),
        ("git.pdf", 1),
        ("imagemagick-lzw.pdf", 1),
        ("imagemagick-ASCII85Decode.pdf", 1),
        ("imagemagick-CCITTFaxDecode.pdf", 1),
    ],
)
def test_get_images(src, nb_images):
    src = os.path.join(RESOURCE_ROOT, src)
    reader = PdfFileReader(src)

    with pytest.raises(TypeError):
        page = reader.pages["0"]

    page = reader.pages[-1]
    page = reader.pages[0]

    images_extracted = []

    if RES.XOBJECT in page[PG.RESOURCES]:
        xObject = page[PG.RESOURCES][RES.XOBJECT].getObject()

        for obj in xObject:
            if xObject[obj][IA.SUBTYPE] == "/Image":
                extension, byte_stream = _xobj_to_image(xObject[obj])
                if extension is not None:
                    filename = obj[1:] + ".png"
                    with open(filename, "wb") as img:
                        img.write(byte_stream)
                    images_extracted.append(filename)

    assert len(images_extracted) == nb_images

    # Cleanup
    for filepath in images_extracted:
        os.remove(filepath)


@pytest.mark.parametrize(
    ("strict", "with_prev_0", "startx_correction", "should_fail"),
    [
        (True, False, -1, False),  # all nominal => no fail
        (True, True, -1, True),  # Prev=0 => fail expected
        (False, False, -1, False),
        (False, True, -1, False),  # Prev =0 => no strict so tolerant
        (True, False, 0, True),  # error on startxref, in strict => fail expected
        (True, True, 0, True),
        (
            False,
            False,
            0,
            False,
        ),  # error on startxref, but no strict => xref rebuilt,no fail
        (False, True, 0, False),
    ],
)
def test_get_images_raw(strict, with_prev_0, startx_correction, should_fail):
    pdf_data = (
        b"%%PDF-1.7\n"
        b"1 0 obj << /Count 1 /Kids [4 0 R] /Type /Pages >> endobj\n"
        b"2 0 obj << >> endobj\n"
        b"3 0 obj << >> endobj\n"
        b"4 0 obj << /Contents 3 0 R /CropBox [0.0 0.0 2550.0 3508.0]"
        b" /MediaBox [0.0 0.0 2550.0 3508.0] /Parent 1 0 R"
        b" /Resources << /Font << >> >>"
        b" /Rotate 0 /Type /Page >> endobj\n"
        b"5 0 obj << /Pages 1 0 R /Type /Catalog >> endobj\n"
        b"xref 1 5\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"trailer << %s/Root 5 0 R /Size 6 >>\n"
        b"startxref %d\n"
        b"%%%%EOF"
    )
    pdf_data = pdf_data % (
        pdf_data.find(b"1 0 obj"),
        pdf_data.find(b"2 0 obj"),
        pdf_data.find(b"3 0 obj"),
        pdf_data.find(b"4 0 obj"),
        pdf_data.find(b"5 0 obj"),
        b"/Prev 0 " if with_prev_0 else b"",
        # startx_correction should be -1 due to double % at the beginning indiducing an error on startxref computation
        pdf_data.find(b"xref") + startx_correction,
    )
    pdf_stream = io.BytesIO(pdf_data)
    if should_fail:
        with pytest.raises(PdfReadError) as exc:
            PdfFileReader(pdf_stream, strict=strict)
        assert exc.type == PdfReadError
        if startx_correction == -1:
            assert (
                exc.value.args[0]
                == "/Prev=0 in the trailer (try opening with strict=False)"
            )
    else:
        PdfFileReader(pdf_stream, strict=strict)


def test_issue297():
    path = os.path.join(RESOURCE_ROOT, "issue-297.pdf")
    with pytest.raises(PdfReadError) as exc:
        reader = PdfFileReader(path, strict=True)
    assert "Broken xref table" in exc.value.args[0]
    reader = PdfFileReader(path, strict=False)
    reader.getPage(0)


def test_get_page_of_encrypted_file():
    """
    Check if we can read a page of an encrypted file.

    This is a regression test for issue 327:
    IndexError for getPage() of decrypted file
    """
    path = os.path.join(RESOURCE_ROOT, "encrypted-file.pdf")
    reader = PdfFileReader(path)

    # Password is correct:)
    reader.decrypt("test")

    reader.getPage(0)


@pytest.mark.parametrize(
    ("src", "expected", "expected_get_fields"),
    [
        (
            "form.pdf",
            {"foo": ""},
            {"foo": {"/DV": "", "/FT": "/Tx", "/T": "foo", "/V": ""}},
        ),
        (
            "form_acrobatReader.pdf",
            {"foo": "Bar"},
            {"foo": {"/DV": "", "/FT": "/Tx", "/T": "foo", "/V": "Bar"}},
        ),
        (
            "form_evince.pdf",
            {"foo": "bar"},
            {"foo": {"/DV": "", "/FT": "/Tx", "/T": "foo", "/V": "bar"}},
        ),
        (
            "crazyones.pdf",
            {},
            None,
        ),
    ],
)
def test_get_form(src, expected, expected_get_fields):
    """Check if we can read out form data."""
    src = os.path.join(RESOURCE_ROOT, src)
    reader = PdfFileReader(src)
    fields = reader.getFormTextFields()
    assert fields == expected

    fields = reader.getFields()
    assert fields == expected_get_fields
    if fields:
        for field in fields.values():
            # Just access the attributes
            [
                field.fieldType,
                field.parent,
                field.kids,
                field.name,
                field.altName,
                field.mappingName,
                field.flags,
                field.value,
                field.defaultValue,
                field.additionalActions,
            ]


@pytest.mark.parametrize(
    ("src", "page_nb"),
    [
        ("form.pdf", 0),
        ("pdflatex-outline.pdf", 2),
    ],
)
def test_get_page_number(src, page_nb):
    src = os.path.join(RESOURCE_ROOT, src)
    reader = PdfFileReader(src)
    page = reader.pages[page_nb]
    assert reader.getPageNumber(page) == page_nb


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        ("form.pdf", None),
    ],
)
def test_get_page_layout(src, expected):
    src = os.path.join(RESOURCE_ROOT, src)
    reader = PdfFileReader(src)
    assert reader.getPageLayout() == expected


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        ("form.pdf", "/UseNone"),
        ("crazyones.pdf", None),
    ],
)
def test_get_page_mode(src, expected):
    src = os.path.join(RESOURCE_ROOT, src)
    reader = PdfFileReader(src)
    assert reader.getPageMode() == expected


def test_read_empty():
    with pytest.raises(PdfReadError) as exc:
        PdfFileReader(io.BytesIO())
    assert exc.value.args[0] == "Cannot read an empty file"


def test_read_malformed_header():
    with pytest.raises(PdfReadError) as exc:
        PdfFileReader(io.BytesIO(b"foo"))
    assert exc.value.args[0] == "PDF starts with 'foo', but '%PDF-' expected"


def test_read_malformed_body():
    with pytest.raises(PdfReadError) as exc:
        PdfFileReader(io.BytesIO(b"%PDF-"))
    assert exc.value.args[0] == "Could not read malformed PDF file"


def test_read_prev_0_trailer():
    pdf_data = (
        b"%%PDF-1.7\n"
        b"1 0 obj << /Count 1 /Kids [4 0 R] /Type /Pages >> endobj\n"
        b"2 0 obj << >> endobj\n"
        b"3 0 obj << >> endobj\n"
        b"4 0 obj << /Contents 3 0 R /CropBox [0.0 0.0 2550.0 3508.0]"
        b" /MediaBox [0.0 0.0 2550.0 3508.0] /Parent 1 0 R"
        b" /Resources << /Font << >> >>"
        b" /Rotate 0 /Type /Page >> endobj\n"
        b"5 0 obj << /Pages 1 0 R /Type /Catalog >> endobj\n"
        b"xref 1 5\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"trailer << %s/Root 5 0 R /Size 6 >>\n"
        b"startxref %d\n"
        b"%%%%EOF"
    )
    with_prev_0 = True
    pdf_data = pdf_data % (
        pdf_data.find(b"1 0 obj"),
        pdf_data.find(b"2 0 obj"),
        pdf_data.find(b"3 0 obj"),
        pdf_data.find(b"4 0 obj"),
        pdf_data.find(b"5 0 obj"),
        b"/Prev 0 " if with_prev_0 else b"",
        pdf_data.find(b"xref") - 1,
    )
    pdf_stream = io.BytesIO(pdf_data)
    with pytest.raises(PdfReadError) as exc:
        PdfFileReader(pdf_stream, strict=True)
    assert exc.value.args[0] == "/Prev=0 in the trailer (try opening with strict=False)"


def test_read_missing_startxref():
    pdf_data = (
        b"%%PDF-1.7\n"
        b"1 0 obj << /Count 1 /Kids [4 0 R] /Type /Pages >> endobj\n"
        b"2 0 obj << >> endobj\n"
        b"3 0 obj << >> endobj\n"
        b"4 0 obj << /Contents 3 0 R /CropBox [0.0 0.0 2550.0 3508.0]"
        b" /MediaBox [0.0 0.0 2550.0 3508.0] /Parent 1 0 R"
        b" /Resources << /Font << >> >>"
        b" /Rotate 0 /Type /Page >> endobj\n"
        b"5 0 obj << /Pages 1 0 R /Type /Catalog >> endobj\n"
        b"xref 1 5\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"trailer << /Root 5 0 R /Size 6 >>\n"
        # b"startxref %d\n"
        b"%%%%EOF"
    )
    pdf_data = pdf_data % (
        pdf_data.find(b"1 0 obj"),
        pdf_data.find(b"2 0 obj"),
        pdf_data.find(b"3 0 obj"),
        pdf_data.find(b"4 0 obj"),
        pdf_data.find(b"5 0 obj"),
        # pdf_data.find(b"xref") - 1,
    )
    pdf_stream = io.BytesIO(pdf_data)
    with pytest.raises(PdfReadError) as exc:
        PdfFileReader(pdf_stream, strict=True)
    assert exc.value.args[0] == "startxref not found"


def test_read_unknown_zero_pages():
    pdf_data = (
        b"%%PDF-1.7\n"
        b"1 0 obj << /Count 1 /Kids [4 0 R] /Type /Pages >> endobj\n"
        b"2 0 obj << >> endobj\n"
        b"3 0 obj << >> endobj\n"
        b"4 0 obj << /Contents 3 0 R /CropBox [0.0 0.0 2550.0 3508.0]"
        b" /MediaBox [0.0 0.0 2550.0 3508.0] /Parent 1 0 R"
        b" /Resources << /Font << >> >>"
        b" /Rotate 0 /Type /Page >> endobj\n"
        # Pages 0 0 is the key point:
        b"5 0 obj << /Pages 0 0 R /Type /Catalog >> endobj\n"
        b"xref 1 5\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"%010d 00000 n\n"
        b"trailer << /Root 5 1 R /Size 6 >>\n"
        b"startxref %d\n"
        b"%%%%EOF"
    )
    pdf_data = pdf_data % (
        pdf_data.find(b"1 0 obj"),
        pdf_data.find(b"2 0 obj"),
        pdf_data.find(b"3 0 obj"),
        pdf_data.find(b"4 0 obj"),
        pdf_data.find(b"5 0 obj"),
        pdf_data.find(b"xref") - 1,
    )
    pdf_stream = io.BytesIO(pdf_data)
    reader = PdfFileReader(pdf_stream, strict=True)
    with pytest.raises(PdfReadError) as exc:
        reader.numPages

    assert exc.value.args[0] == "Could not find object."
    reader = PdfFileReader(pdf_stream, strict=False)
    with pytest.raises(AttributeError) as exc:
        reader.numPages
    assert exc.value.args[0] == "'NoneType' object has no attribute 'getObject'"


def test_read_encrypted_without_decryption():
    src = os.path.join(RESOURCE_ROOT, "libreoffice-writer-password.pdf")
    reader = PdfFileReader(src)
    with pytest.raises(PdfReadError) as exc:
        reader.numPages
    assert exc.value.args[0] == "File has not been decrypted"


def test_get_destination_age_number():
    src = os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf")
    reader = PdfFileReader(src)
    outlines = reader.getOutlines()
    for outline in outlines:
        if not isinstance(outline, list):
            reader.getDestinationPageNumber(outline)


def test_do_not_get_stuck_on_large_files_without_start_xref():
    """Tests for the absence of a DoS bug, where a large file without an startxref mark
    would cause the library to hang for minutes to hours"""
    start_time = time.time()
    broken_stream = StreamIO(b"\0" * 5 * 1000 * 1000)
    with pytest.raises(PdfReadError):
        PdfFileReader(broken_stream)
    parse_duration = time.time() - start_time
    # parsing is expected take less than a second on a modern cpu, but include a large
    # tolerance to account for busy or slow systems
    assert parse_duration < 60


def test_PdfReaderDecryptWhenNoID():
    """
    Decrypt an encrypted file that's missing the 'ID' value in its
    trailer.
    https://github.com/mstamy2/PyPDF2/issues/608
    """

    with open(
        os.path.join(RESOURCE_ROOT, "encrypted_doc_no_id.pdf"), "rb"
    ) as inputfile:
        ipdf = PdfFileReader(inputfile)
        ipdf.decrypt("")
        assert ipdf.getDocumentInfo() == {"/Producer": "European Patent Office"}


def test_reader_properties():
    reader = PdfFileReader(os.path.join(RESOURCE_ROOT, "crazyones.pdf"))
    assert reader.outlines == []
    assert len(reader.pages) == 1
    assert reader.pageLayout is None
    assert reader.pageMode is None
    assert reader.isEncrypted is False


@pytest.mark.parametrize(
    "strict",
    [(True), (False)],
)
def test_issue604(strict):
    """
    Test with invalid destinations
    """
    with open(os.path.join(RESOURCE_ROOT, "issue-604.pdf"), "rb") as f:
        pdf = None
        bookmarks = None
        if strict:
            with pytest.raises(PdfReadError) as exc:
                pdf = PdfFileReader(f, strict=strict)
                bookmarks = pdf.getOutlines()
            if "Unknown Destination" not in exc.value.args[0]:
                raise Exception("Expected exception not raised")
            return  # bookmarks not correct
        else:
            pdf = PdfFileReader(f, strict=strict)
            bookmarks = pdf.getOutlines()

        def getDestPages(x):
            # print(x)
            if isinstance(x, list):
                r = [getDestPages(y) for y in x]
                return r
            else:
                return pdf.getDestinationPageNumber(x) + 1

        out = []
        for (
            b
        ) in bookmarks:  # b can be destination or a list:preferred to just print them
            out.append(getDestPages(b))
    # print(out)


def test_decode_permissions():
    reader = PdfFileReader(os.path.join(RESOURCE_ROOT, "crazyones.pdf"))
    base = {
        "accessability": False,
        "annotations": False,
        "assemble": False,
        "copy": False,
        "forms": False,
        "modify": False,
        "print_high_quality": False,
        "print": False,
    }

    print_ = base.copy()
    print_["print"] = True
    assert reader.decode_permissions(4) == print_

    modify = base.copy()
    modify["modify"] = True
    assert reader.decode_permissions(8) == modify
