import os
import pytest
import PyPDF2

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


@pytest.mark.parametrize(
    "src",
    [
        (os.path.join(RESOURCE_ROOT, "crazyones.pdf")),
        (os.path.join(RESOURCE_ROOT, "commented.pdf")),
    ],
)
def test_get_annotations(src):
    reader = PyPDF2.PdfFileReader(open(src, "rb"))

    for i in range(reader.getNumPages()):
        page = reader.getPage(i)
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
