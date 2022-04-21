import io
import os

import pytest

from PyPDF2 import PdfFileReader
from PyPDF2.constants import ImageAttributes as IA
from PyPDF2.constants import PageAttributes as PG
from PyPDF2.constants import Ressources as RES
from PyPDF2.errors import PdfReadError
from PyPDF2.filters import _xobj_to_image

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


@pytest.mark.parametrize(
    "src,num_pages", [("selenium-PyPDF2-issue-177.pdf", 1), ("pdflatex-outline.pdf", 4)]
)
def test_get_num_pages(src, num_pages):
    src = os.path.join(RESOURCE_ROOT, src)
    reader = PdfFileReader(src)
    assert reader.getNumPages() == num_pages


@pytest.mark.parametrize(
    "pdf_path, expected",
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
        docinfo = reader.getDocumentInfo()
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
                    annot.getObject()["/Contents"]


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
    for i in range(reader.getNumPages()):
        page = reader.getPage(i)
        if PG.ANNOTS in page:
            for annotation in page[PG.ANNOTS]:
                annotobj = annotation.getObject()
                if annotobj[IA.SUBTYPE] == "/FileAttachment":
                    fileobj = annotobj["/FS"]
                    attachments[fileobj["/F"]] = fileobj["/EF"]["/F"].getData()
    return attachments


@pytest.mark.parametrize(
    "src,outline_elements",
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
    "src,nb_images",
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
    "strict,with_prev_0,should_fail",
    [
        (True, True, True),
        (True, False, False),
        (False, True, False),
        (False, False, False),
    ],
)
def test_get_images_raw(strict, with_prev_0, should_fail):
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
        pdf_data.find(b"xref"),
    )
    pdf_stream = io.BytesIO(pdf_data)
    if should_fail:
        with pytest.raises(PdfReadError) as exc:
            PdfFileReader(pdf_stream, strict=strict)
        assert (
            exc.value.args[0]
            == "/Prev=0 in the trailer (try opening with strict=False)"
        )
    else:
        PdfFileReader(pdf_stream, strict=strict)


@pytest.mark.xfail(
    reason=(
        "It's still broken - and unclear what the issue is. "
        "Help would be appreciated!"
    )
)
def test_issue297():
    path = os.path.join(RESOURCE_ROOT, "issue-297.pdf")
    reader = PdfFileReader(path, "rb")
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
    "src,expected,expected_method",
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
    ],
)
def test_get_form(src, expected, expected_method):
    """Check if we can read out form data."""
    src = os.path.join(RESOURCE_ROOT, src)
    reader = PdfFileReader(src)
    fields = reader.getFormTextFields()
    assert fields == expected

    fields = reader.getFields()
    assert fields == expected_method


@pytest.mark.parametrize(
    "src,page_nb",
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
    "src,expected",
    [
        ("form.pdf", None),
    ],
)
def test_get_page_layout(src, expected):
    src = os.path.join(RESOURCE_ROOT, src)
    reader = PdfFileReader(src)
    assert reader.getPageLayout() == expected


@pytest.mark.parametrize(
    "src,expected",
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


def test_read_malformed():
    with pytest.raises(PdfReadError) as exc:
        PdfFileReader(io.BytesIO(b"foo"))
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
        pdf_data.find(b"xref"),
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
        # pdf_data.find(b"xref"),
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
        pdf_data.find(b"xref"),
    )
    pdf_stream = io.BytesIO(pdf_data)
    with pytest.raises(PdfReadError) as exc:
        reader = PdfFileReader(pdf_stream, strict=True)
        reader.getNumPages()

    assert exc.value.args[0] == "Could not find object."
    reader = PdfFileReader(pdf_stream, strict=False)
    with pytest.raises(AttributeError) as exc:
        reader.getNumPages()
    assert exc.value.args[0] == "'NoneType' object has no attribute 'getObject'"


def test_read_encrypted_without_decryption():
    src = os.path.join(RESOURCE_ROOT, "libreoffice-writer-password.pdf")
    reader = PdfFileReader(src)
    with pytest.raises(PdfReadError) as exc:
        reader.getNumPages()
    assert exc.value.args[0] == "File has not been decrypted"


def test_get_destination_age_number():
    src = os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf")
    reader = PdfFileReader(src)
    outlines = reader.getOutlines()
    for outline in outlines:
        if not isinstance(outline, list):
            reader.getDestinationPageNumber(outline)
