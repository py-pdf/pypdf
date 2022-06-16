import os
import sys

import PyPDF2
from PyPDF2.generic import Destination

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "resources")

sys.path.append(PROJECT_ROOT)


def test_merge():
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    outline = os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf")
    pdf_forms = os.path.join(RESOURCE_ROOT, "pdflatex-forms.pdf")
    pdf_pw = os.path.join(RESOURCE_ROOT, "libreoffice-writer-password.pdf")

    merger = PyPDF2.PdfMerger()

    # string path:
    merger.append(pdf_path)
    merger.append(outline)
    merger.append(pdf_path, pages=PyPDF2.pagerange.PageRange(slice(0, 0)))
    merger.append(pdf_forms)

    # Merging an encrypted file
    reader = PyPDF2.PdfReader(pdf_pw)
    reader.decrypt("openpassword")
    merger.append(reader)

    # PdfReader object:
    merger.append(PyPDF2.PdfReader(pdf_path), bookmark="foo")

    # File handle
    with open(pdf_path, "rb") as fh:
        merger.append(fh)

    bookmark = merger.add_bookmark("A bookmark", 0)
    bm2 = merger.add_bookmark("deeper", 1, parent=bookmark, italic=True, bold=True)
    merger.add_bookmark(
        "Let's see", merger.pages[2], bm2, (255, 255, 0), True, True, "/FitBV", 12
    )
    merger.add_bookmark(
        "The XYZ fit", 0, bookmark, (255, 0, 15), True, True, "/XYZ", 10, 20, 3
    )
    merger.add_bookmark(
        "The FitH fit", 0, bookmark, (255, 0, 15), True, True, "/FitH", 10
    )
    merger.add_bookmark(
        "The FitV fit", 0, bookmark, (255, 0, 15), True, True, "/FitV", 10
    )
    merger.add_bookmark(
        "The FitR fit", 0, bookmark, (255, 0, 15), True, True, "/FitR", 10, 20, 30, 40
    )
    merger.add_bookmark("The FitB fit", 0, bookmark, (255, 0, 15), True, True, "/FitB")
    merger.add_bookmark(
        "The FitBH fit", 0, bookmark, (255, 0, 15), True, True, "/FitBH", 10
    )
    merger.add_bookmark(
        "The FitBV fit", 0, bookmark, (255, 0, 15), True, True, "/FitBV", 10
    )
    merger.add_metadata({"author": "Martin Thoma"})
    merger.add_named_destination("title", 0)
    merger.set_page_layout("/SinglePage")
    merger.set_page_mode("/UseThumbs")

    tmp_path = "dont_commit_merged.pdf"
    merger.write(tmp_path)
    merger.close()

    # Check if bookmarks are correct
    reader = PyPDF2.PdfReader(tmp_path)
    assert [
        el.title for el in reader._get_outlines() if isinstance(el, Destination)
    ] == [
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
        "foo",
    ]

    # TODO: There seem to be no destionations for those links?

    # Clean up
    os.remove(tmp_path)
