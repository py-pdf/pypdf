import io
import os
import pytest
import PyPDF2
from PyPDF2.filters import decodeStreamData, _xobj_to_image

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


def test_read_metadata():
    with open(os.path.join(RESOURCE_ROOT, "crazyones.pdf"), "rb") as inputfile:
        ipdf = PyPDF2.PdfFileReader(inputfile)
        metadict = ipdf.getDocumentInfo()
        assert metadict.title is None
        assert dict(metadict) == {
            "/CreationDate": "D:20150604133406-06'00'",
            "/Creator": " XeTeX output 2015.06.04:1334",
            "/Producer": "xdvipdfmx (20140317)",
        }


@pytest.mark.parametrize(
    "src",
    [
        (os.path.join(RESOURCE_ROOT, "crazyones.pdf")),
        (os.path.join(RESOURCE_ROOT, "commented.pdf")),
    ],
)
def test_get_annotations(src):
    reader = PyPDF2.PdfFileReader(open(src, "rb"))

    for page in reader.pages:
        print("/Annots" in page)
        if "/Annots" in page:
            for annot in page["/Annots"]:
                subtype = annot.getObject()["/Subtype"]
                if subtype == "/Text":
                    print(annot.getObject()["/Contents"])
                    print("")


@pytest.mark.parametrize(
    "src",
    [
        (os.path.join(RESOURCE_ROOT, "attachment.pdf")),
        (os.path.join(RESOURCE_ROOT, "crazyones.pdf")),
    ],
)
def test_get_attachments(src):
    reader = PyPDF2.PdfFileReader(open(src, "rb"))

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
    reader = PyPDF2.PdfFileReader(open(src, "rb"))
    outlines = reader.getOutlines()
    assert len(outlines) == outline_elements


@pytest.mark.parametrize(
    "src,nb_images",
    [
        (os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf"), 0),
        (os.path.join(RESOURCE_ROOT, "crazyones.pdf"), 0),
        (os.path.join(RESOURCE_ROOT, "git.pdf"), 1),
    ],
)
def test_get_images(src, nb_images):
    reader = PyPDF2.PdfFileReader(open(src, "rb"))

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
    else:
        print("No image found.")

    assert len(images_extracted) == nb_images


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
    pdf_data = b"%%PDF-1.7\n" \
               b"1 0 obj << /Count 1 /Kids [4 0 R] /Type /Pages >> endobj\n" \
               b"2 0 obj << >> endobj\n" \
               b"3 0 obj << >> endobj\n" \
               b"4 0 obj << /Contents 3 0 R /CropBox [0.0 0.0 2550.0 3508.0]" \
               b" /MediaBox [0.0 0.0 2550.0 3508.0] /Parent 1 0 R" \
               b" /Resources << /Font << >> >>" \
               b" /Rotate 0 /Type /Page >> endobj\n" \
               b"5 0 obj << /Pages 1 0 R /Type /Catalog >> endobj\n" \
               b"xref 1 5\n" \
               b"%010d 00000 n\n" \
               b"%010d 00000 n\n" \
               b"%010d 00000 n\n" \
               b"%010d 00000 n\n" \
               b"%010d 00000 n\n" \
               b"trailer << %s/Root 5 0 R /Size 6 >>\n" \
               b"startxref %d\n" \
               b"%%%%EOF"
    pdf_data = pdf_data % (pdf_data.find(b"1 0 obj"),
                           pdf_data.find(b"2 0 obj"),
                           pdf_data.find(b"3 0 obj"),
                           pdf_data.find(b"4 0 obj"),
                           pdf_data.find(b"5 0 obj"),
                           b"/Prev 0 " if with_prev_0 else b"",
                           pdf_data.find(b"xref"),
                           )
    pdf_stream = io.BytesIO(pdf_data)
    if should_fail:
        with pytest.raises(PyPDF2.pdf.utils.PdfReadError):
            PyPDF2.PdfFileReader(pdf_stream, strict=strict)
    else:
        PyPDF2.PdfFileReader(pdf_stream, strict=strict)
