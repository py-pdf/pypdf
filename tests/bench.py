import os

import pytest

import PyPDF2
from PyPDF2 import PdfReader, Transformation
from PyPDF2.generic import Destination

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "resources")
SAMPLE_ROOT = os.path.join(PROJECT_ROOT, "sample-files")


def page_ops(pdf_path, password):
    pdf_path = os.path.join(RESOURCE_ROOT, pdf_path)

    reader = PdfReader(pdf_path)

    if password:
        reader.decrypt(password)

    page = reader.pages[0]

    op = Transformation().rotate(90).scale(1.2)
    page.add_transformation(op)
    page.merge_page(page)

    op = Transformation().scale(1).translate(tx=1, ty=1)
    page.add_transformation(op)
    page.merge_page(page)

    op = Transformation().rotate(90).scale(1).translate(tx=1, ty=1)
    page.add_transformation(op)
    page.merge_page(page)

    page.add_transformation((1, 0, 0, 0, 0, 0))
    page.scale(2, 2)
    page.scale_by(0.5)
    page.scale_to(100, 100)
    page.compress_content_streams()
    page.extract_text()


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

    file_merger = PyPDF2.PdfMerger()

    # string path:
    file_merger.append(pdf_path)
    file_merger.append(outline)
    file_merger.append(pdf_path, pages=PyPDF2.pagerange.PageRange(slice(0, 0)))
    file_merger.append(pdf_forms)

    # Merging an encrypted file
    reader = PyPDF2.PdfReader(pdf_pw)
    reader.decrypt("openpassword")
    file_merger.append(reader)

    # PdfReader object:
    file_merger.append(PyPDF2.PdfReader(pdf_path, "rb"), outline_item=True)

    # File handle
    with open(pdf_path, "rb") as fh:
        file_merger.append(fh)

    outline_item = file_merger.add_outline_item("An outline item", 0)
    file_merger.add_outline_item("deeper", 0, parent=outline_item)
    file_merger.add_metadata({"author": "Martin Thoma"})
    file_merger.add_named_destination("title", 0)
    file_merger.set_page_layout("/SinglePage")
    file_merger.set_page_mode("/UseThumbs")

    tmp_path = "dont_commit_merged.pdf"
    file_merger.write(tmp_path)
    file_merger.close()

    # Check if outline is correct
    reader = PyPDF2.PdfReader(tmp_path)
    assert [
        el.title for el in reader._get_outline() if isinstance(el, Destination)
    ] == [
        "An outline item",
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


def text_extraction(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


@pytest.mark.filterwarnings("ignore::PyPDF2.errors.PdfReadWarning")
def test_text_extraction(benchmark):
    file_path = os.path.join(SAMPLE_ROOT, "009-pdflatex-geotopo/GeoTopo.pdf")
    benchmark(text_extraction, file_path)
