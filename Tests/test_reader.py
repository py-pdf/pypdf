import io
import os

import pytest

import PyPDF2.utils
from PyPDF2 import PdfFileReader
from PyPDF2.filters import _xobj_to_image

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


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
        metadict = reader.getDocumentInfo()
        assert dict(metadict) == expected


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
        if "/Annots" in page:
            for annot in page["/Annots"]:
                subtype = annot.getObject()["/Subtype"]
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
        if "/Annots" in page:
            for annotation in page["/Annots"]:
                annotobj = annotation.getObject()
                if annotobj["/Subtype"] == "/FileAttachment":
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
        (os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf"), 0),
        (os.path.join(RESOURCE_ROOT, "crazyones.pdf"), 0),
        (os.path.join(RESOURCE_ROOT, "git.pdf"), 1),
        (os.path.join(RESOURCE_ROOT, "imagemagick-lzw.pdf"), 1),
    ],
)
def test_get_images(src, nb_images):
    reader = PdfFileReader(src)

    with pytest.raises(TypeError):
        page = reader.pages["0"]

    page = reader.pages[-1]
    page = reader.pages[0]

    images_extracted = []

    if "/XObject" in page["/Resources"]:
        xObject = page["/Resources"]["/XObject"].getObject()

        for obj in xObject:
            if xObject[obj]["/Subtype"] == "/Image":
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
        with pytest.raises(PyPDF2.utils.PdfReadError):
            PdfFileReader(pdf_stream, strict=strict)
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
