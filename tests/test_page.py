import json
import os
import copy
import io

import pytest

from PyPDF2 import PdfFileReader,PdfFileWriter
from PyPDF2._page import PageObject
from PyPDF2.generic import RectangleObject

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "resources")
EXTERNAL_ROOT = os.path.join(PROJECT_ROOT, "sample-files")


def get_all_sample_files():
    with open(os.path.join(EXTERNAL_ROOT, "files.json")) as fp:
        data = fp.read()
    meta = json.loads(data)
    return meta


all_files_meta = get_all_sample_files()


@pytest.mark.external()
@pytest.mark.parametrize(
    "meta",
    [m for m in all_files_meta["data"] if not m["encrypted"]],
    ids=[m["path"] for m in all_files_meta["data"] if not m["encrypted"]],
)
def test_read(meta):
    pdf_path = os.path.join(EXTERNAL_ROOT, meta["path"])
    reader = PdfFileReader(pdf_path)
    reader.pages[0]
    assert len(reader.pages) == meta["pages"]


@pytest.mark.parametrize(
    ("pdf_path", "password"),
    [
        ("crazyones.pdf", None),
        ("attachment.pdf", None),
        # ("side-by-side-subfig.pdf", None),
        (
            "libreoffice-writer-password.pdf",
            "openpassword",
        ),
        ("imagemagick-images.pdf", None),
        ("imagemagick-lzw.pdf", None),
        ("reportlab-inline-image.pdf", None),
    ],
)
def test_page_operations(pdf_path, password):
    """
    This test just checks if the operation throws an exception.

    This should be done way more thoroughly: It should be checked if the
    output is as expected.
    """
    pdf_path = os.path.join(RESOURCE_ROOT, pdf_path)
    reader = PdfFileReader(pdf_path)

    if password:
        reader.decrypt(password)

    page: PageObject = reader.pages[0]
    page.mergeRotatedScaledTranslatedPage(page, 90, scale=1, tx=1, ty=1, expand=True)
    page.addTransformation([1, 0, 0, 0, 0, 0])
    page.scale(2, 2)
    page.scaleBy(0.5)
    page.scaleTo(100, 100)
    page.compressContentStreams()
    page.extractText()


def test_page_transformations():
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    reader = PdfFileReader(pdf_path)

    page: PageObject = reader.pages[0]
    page.mergeRotatedPage(page, 90, expand=True)
    page.mergeRotatedScaledPage(page, 90, 1, expand=True)
    page.mergeRotatedScaledTranslatedPage(page, 90, scale=1, tx=1, ty=1, expand=True)
    page.mergeRotatedTranslatedPage(page, 90, 100, 100, expand=False)
    page.mergeScaledPage(page, 2, expand=False)
    page.mergeScaledTranslatedPage(page, 1, 1, 1)
    page.mergeTranslatedPage(page, 100, 100, expand=False)
    page.addTransformation([1, 0, 0, 0, 0, 0])


@pytest.mark.parametrize(
    ("pdf_path", "password"),
    [
        (os.path.join(RESOURCE_ROOT, "crazyones.pdf"), None),
        (os.path.join(RESOURCE_ROOT, "attachment.pdf"), None),
        (os.path.join(RESOURCE_ROOT, "side-by-side-subfig.pdf"), None),
        (
            os.path.join(RESOURCE_ROOT, "libreoffice-writer-password.pdf"),
            "openpassword",
        ),
    ],
)
def test_compress_content_streams(pdf_path, password):
    reader = PdfFileReader(pdf_path)
    if password:
        reader.decrypt(password)
    for page in reader.pages:
        page.compressContentStreams()


def test_page_properties():
    reader = PdfFileReader(os.path.join(RESOURCE_ROOT, "crazyones.pdf"))
    page = reader.pages[0]
    assert page.mediaBox == RectangleObject([0, 0, 612, 792])
    assert page.cropBox == RectangleObject([0, 0, 612, 792])
    assert page.bleedBox == RectangleObject([0, 0, 612, 792])
    assert page.trimBox == RectangleObject([0, 0, 612, 792])
    assert page.artBox == RectangleObject([0, 0, 612, 792])

    page.bleedBox = RectangleObject([0, 1, 100, 101])
    assert page.bleedBox == RectangleObject([0, 1, 100, 101])


def test_page_rotation_non90():
    reader = PdfFileReader(os.path.join(RESOURCE_ROOT, "crazyones.pdf"))
    page = reader.pages[0]
    with pytest.raises(ValueError) as exc:
        page.rotateClockwise(91)
    assert exc.value.args[0] == "Rotation angle must be a multiple of 90"

def test_page_merge_cropped():
    p = PdfFileReader(os.path.join(RESOURCE_ROOT, "issue-604.pdf"))
    a=  copy.deepcopy(p.getPage(1))     # crossed to ease test reading
    b=  copy.deepcopy(p.getPage(2))
    a.cropBox = RectangleObject([100,100,300,200])
    w = PdfFileWriter()
    w.addPage(a)
    w.addPage(b)
    c=copy.deepcopy(b)
    c.mergePage(a)
    w.addPage(c)
    o = io.BytesIO()
    w.write(o)
