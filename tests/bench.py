"""
Benchmark the speed of pypdf.

The results are on https://py-pdf.github.io/pypdf/dev/bench/
Please keep in mind that the variance is high.
"""
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

import pypdf
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf._page import PageObject
from pypdf.generic import Destination, read_string_from_stream

from . import get_data_from_url

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

    writer = PdfWriter()

    # string path:
    writer.append(pdf_path)
    writer.append(outline)
    writer.append(pdf_path, pages=pypdf.pagerange.PageRange(slice(0, 0)))
    writer.append(pdf_forms)

    # Merging an encrypted file
    reader = PdfReader(pdf_pw)
    reader.decrypt("openpassword")
    writer.append(reader)

    # PdfReader object:
    writer.append(PdfReader(pdf_path, "rb"), outline_item="True")

    # File handle
    with open(pdf_path, "rb") as fh:
        writer.append(fh)

    outline_item = writer.add_outline_item("An outline item", 0)
    writer.add_outline_item("deeper", 0, parent=outline_item)
    writer.add_metadata({"/Author": "Martin Thoma"})
    writer.add_named_destination("title", 0)
    writer.set_page_layout("/SinglePage")
    writer.page_mode = "/UseThumbs"

    with NamedTemporaryFile(suffix=".pdf") as target_file:
        write_path = target_file.name
        writer.write(write_path)
        writer.close()

        # Check if outline is correct
        reader = PdfReader(write_path)
        assert [
            el.title for el in reader._get_outline() if isinstance(el, Destination)
        ] == [
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
            "An outline item",
        ]


def test_merge(benchmark):
    """
    Apply various page operations.

    Rotation, scaling, translation, content stream compression, text extraction
    """
    benchmark(merge)


def text_extraction(pdf_path):
    with open(pdf_path, mode="rb") as fd:
        reader = PdfReader(fd)
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


def image_new_property(data):
    reader = PdfReader(data)
    assert reader.pages[0].images.keys() == [
        "/I0",
        "/I1",
        "/I2",
        "/I3",
        "/I4",
        "/I5",
        "/I6",
        "/I7",
        "/I8",
        "/I9",
        ["/TPL1", "/Image5"],
        ["/TPL2", "/Image53"],
        ["/TPL2", "/Image37"],
        ["/TPL2", "/Image49"],
        ["/TPL2", "/Image51"],
        ["/TPL2", "/Image39"],
        ["/TPL2", "/Image57"],
        ["/TPL2", "/Image55"],
        ["/TPL2", "/Image43"],
        ["/TPL2", "/Image30"],
        ["/TPL2", "/Image22"],
        ["/TPL2", "/Image41"],
        ["/TPL2", "/Image47"],
        ["/TPL2", "/Image45"],
        ["/TPL3", "/Image65"],
        ["/TPL3", "/Image30"],
        ["/TPL3", "/Image61"],
        ["/TPL4", "/Image30"],
        ["/TPL5", "/Image30"],
        ["/TPL6", "/Image30"],
        ["/TPL7", "/Image30"],
        ["/TPL8", "/Image30"],
        ["/TPL9", "/Image30"],
        ["/TPL10", "/Image30"],
        ["/TPL11", "/Image30"],
        ["/TPL12", "/Image30"],
    ]
    assert len(reader.pages[0].images.items()) == 36
    assert reader.pages[0].images[0].name == "I0.png"
    assert len(reader.pages[0].images[-1].data) == 15168
    assert reader.pages[0].images["/TPL1", "/Image5"].image.format == "JPEG"
    assert (
        reader.pages[0].images["/I0"].indirect_reference.get_object()
        == reader.pages[0]["/Resources"]["/XObject"]["/I0"]
    )
    list(reader.pages[0].images[0:2])
    with pytest.raises(TypeError):
        reader.pages[0].images[b"0"]
    with pytest.raises(IndexError):
        reader.pages[0].images[9999]
    # just for test coverage:
    with pytest.raises(KeyError):
        reader.pages[0]._get_image(["test"], reader.pages[0])
    assert list(PageObject(None, None).images) == []


@pytest.mark.enable_socket
def test_image_new_property_performance(benchmark):
    url = "https://github.com/py-pdf/pypdf/files/11219022/pdf_font_garbled.pdf"
    name = "pdf_font_garbled.pdf"
    data = BytesIO(get_data_from_url(url, name=name))

    benchmark(image_new_property, data)


def image_extraction(data):
    reader = PdfReader(data)
    list(reader.pages[0].images)


@pytest.mark.enable_socket
def test_large_compressed_image_performance(benchmark):
    url = "https://github.com/py-pdf/pypdf/files/15306199/file_with_large_compressed_image.pdf"
    data = BytesIO(get_data_from_url(url, name="file_with_large_compressed_image.pdf"))
    benchmark(image_extraction, data)
