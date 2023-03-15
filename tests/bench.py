"""
Benchmark the speed of pypdf.

The results are on https://py-pdf.github.io/pypdf/dev/bench/
Please keep in mind that the variance is high.
"""
from io import BytesIO
from pathlib import Path

import pypdf
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import Destination, read_string_from_stream

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
SAMPLE_ROOT = PROJECT_ROOT / "sample-files"


def page_ops(pdf_path, password):
    pdf_path = RESOURCE_ROOT / pdf_path

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    if password:
        reader.decrypt(password)

    page = reader.pages[0]
    writer.add_page(page)

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

    page = writer.pages[0]
    page.compress_content_streams()
    page.extract_text()


def test_page_operations(benchmark):
    """
    Apply various page operations.

    Rotation, scaling, translation, content stream compression, text extraction
    """
    benchmark(page_ops, "libreoffice-writer-password.pdf", "openpassword")


def merge():
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    outline = RESOURCE_ROOT / "pdflatex-outline.pdf"
    pdf_forms = RESOURCE_ROOT / "pdflatex-forms.pdf"
    pdf_pw = RESOURCE_ROOT / "libreoffice-writer-password.pdf"

    merger = pypdf.PdfMerger()

    # string path:
    merger.append(pdf_path)
    merger.append(outline)
    merger.append(pdf_path, pages=pypdf.pagerange.PageRange(slice(0, 0)))
    merger.append(pdf_forms)

    # Merging an encrypted file
    reader = pypdf.PdfReader(pdf_pw)
    reader.decrypt("openpassword")
    merger.append(reader)

    # PdfReader object:
    merger.append(pypdf.PdfReader(pdf_path, "rb"), outline_item=True)

    # File handle
    with open(pdf_path, "rb") as fh:
        merger.append(fh)

    outline_item = merger.add_outline_item("An outline item", 0)
    merger.add_outline_item("deeper", 0, parent=outline_item)
    merger.add_metadata({"author": "Martin Thoma"})
    merger.add_named_destination("title", 0)
    merger.set_page_layout("/SinglePage")
    merger.set_page_mode("/UseThumbs")

    write_path = "dont_commit_merged.pdf"
    merger.write(write_path)
    merger.close()

    # Check if outline is correct
    reader = pypdf.PdfReader(write_path)
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


def test_text_extraction(benchmark):
    file_path = SAMPLE_ROOT / "009-pdflatex-geotopo/GeoTopo.pdf"
    benchmark(text_extraction, file_path)


def read_string_from_stream_performance():
    stream = BytesIO(b"(" + b"".join([b"x"] * 1024 * 256) + b")")
    assert read_string_from_stream(stream)


def test_read_string_from_stream_performance(benchmark):
    """
    This test simulates reading an embedded base64 image of 256kb.
    It should be faster than a second, even on ancient machines.

    Runs < 100ms on a 2019 notebook. Takes 10 seconds prior to #1350.
    """
    benchmark(read_string_from_stream_performance)
