import os

import PyPDF2
from PyPDF2 import PdfFileReader
from PyPDF2.generic import Destination

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


def page_ops(pdf_path, password):
    pdf_path = os.path.join(RESOURCE_ROOT, pdf_path)

    reader = PdfFileReader(pdf_path)

    if password:
        reader.decrypt(password)

    page = reader.pages[0]
    page.mergeRotatedScaledPage(page, 90, 1, 1)
    page.mergeScaledTranslatedPage(page, 1, 1, 1)
    page.mergeRotatedScaledTranslatedPage(page, 90, 1, 1, 1, 1)
    page.addTransformation([1, 0, 0, 0, 0, 0])
    page.scale(2, 2)
    page.scaleBy(0.5)
    page.scaleTo(100, 100)
    page.compressContentStreams()
    page.extractText()


def test_page_operations(benchmark):
    """
    Apply various page operations.

    Rotation, scaling, translation, content stream compression, text extraction
    """
    benchmark(page_ops, "libreoffice-writer-password.pdf", "openpassword")


def merge():
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    outline = os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf")
    pdf_forms = os.path.join(RESOURCE_ROOT, "pdflatex-forms.pdf")
    pdf_pw = os.path.join(RESOURCE_ROOT, "libreoffice-writer-password.pdf")

    file_merger = PyPDF2.PdfFileMerger()

    # string path:
    file_merger.append(pdf_path)
    file_merger.append(outline)
    file_merger.append(pdf_path, pages=PyPDF2.pagerange.PageRange(slice(0, 0)))
    file_merger.append(pdf_forms)

    # Merging an encrypted file
    pdfr = PyPDF2.PdfFileReader(pdf_pw)
    pdfr.decrypt("openpassword")
    file_merger.append(pdfr)

    # PdfFileReader object:
    file_merger.append(PyPDF2.PdfFileReader(pdf_path, "rb"), bookmark=True)

    # File handle
    with open(pdf_path, "rb") as fh:
        file_merger.append(fh)

    bookmark = file_merger.addBookmark("A bookmark", 0)
    file_merger.addBookmark("deeper", 0, parent=bookmark)
    file_merger.addMetadata({"author": "Martin Thoma"})
    file_merger.addNamedDestination("title", 0)
    file_merger.setPageLayout("/SinglePage")
    file_merger.setPageMode("/UseThumbs")

    tmp_path = "dont_commit_merged.pdf"
    file_merger.write(tmp_path)
    file_merger.close()

    # Check if bookmarks are correct
    pdfr = PyPDF2.PdfFileReader(tmp_path)
    assert [el.title for el in pdfr.getOutlines() if isinstance(el, Destination)] == [
        "A bookmark",
        "Foo",
        "Bar",
        "Baz",
        "Foo",
        "Bar",
        "Baz",
        "Foo",
        "Bar",
        "Baz",
        "True",
    ]

    # Clean up
    os.remove(tmp_path)


def test_merge(benchmark):
    """
    Apply various page operations.

    Rotation, scaling, translation, content stream compression, text extraction
    """
    benchmark(merge)
