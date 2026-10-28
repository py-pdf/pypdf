"""
Benchmark the speed of pypdf.

The results are on https://py-pdf.github.io/pypdf/dev/bench/

Absolute timings depend heavily on the machine, and GitHub Actions runners
differ by a factor of two. Hence every benchmark is divided by
``test_calibration``, a fixed workload which does not use pypdf. Run

    make benchmark

to get the calibrated values for your machine. They are comparable to the
published ones.

Keep file access and assertions out of the benchmarked functions: they only
add noise.
"""
import re
import zlib
from io import BytesIO

import pytest

import pypdf
from pypdf import PdfReader, PdfWriter, Transformation, apply_configuration
from pypdf.generic import Destination, read_string_from_stream

from . import RESOURCE_ROOT, SAMPLE_ROOT, get_data_from_url

CALIBRATION_DATA = b"".join(
    b"/Key%d %d 0 R [%d %d.5 (text %d)] << /Type /Page >>\n" % (i, i, i, i, i)
    for i in range(5000)
)


def calibration_workload():
    """
    Do pypdf-like work without pypdf: tokenizing bytes, dictionaries, zlib, regular expressions.

    Never change this function, as all published results are relative to it.
    """
    raw = zlib.decompress(zlib.compress(CALIBRATION_DATA))
    stream = BytesIO(raw)
    tokens = []
    current = []
    while True:
        char = stream.read(1)
        if not char:
            break
        if char in b" \n[]()<>/":
            if current:
                tokens.append(b"".join(current))
                current = []
        else:
            current.append(char)
    counts = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    numbers = [int(token) for token in tokens if token.isdigit()]
    names = re.findall(rb"/(\w+)", raw)
    text = "".join(token.decode("latin-1") for token in tokens)
    return len(counts) + sum(numbers) + len(names) + len(text)


def test_calibration(benchmark):
    benchmark(calibration_workload)


def page_ops(data, password):
    reader = PdfReader(BytesIO(data))
    writer = PdfWriter()

    if password:
        reader.decrypt(password)

    page = reader.pages[0]
    page = writer.add_page(page)

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


@apply_configuration(disable_legacy_handling=True)
def test_page_operations(benchmark):
    """
    Apply various page operations.

    Rotation, scaling, translation, content stream compression, text extraction
    """
    data = (RESOURCE_ROOT / "libreoffice-writer-password.pdf").read_bytes()
    benchmark(page_ops, data, "openpassword")


def merge(crazyones, outline, forms, password):
    writer = PdfWriter()

    writer.append(BytesIO(crazyones))
    writer.append(BytesIO(outline))
    writer.append(BytesIO(crazyones), pages=pypdf.pagerange.PageRange(slice(0, 0)))
    writer.append(BytesIO(forms))

    # Merging an encrypted file
    reader = PdfReader(BytesIO(password))
    reader.decrypt("openpassword")
    writer.append(reader)

    # PdfReader object:
    writer.append(PdfReader(BytesIO(crazyones)), outline_item="True")
    writer.append(BytesIO(crazyones))

    outline_item = writer.add_outline_item("An outline item", 0)
    writer.add_outline_item("deeper", 0, parent=outline_item)
    writer.add_metadata({"/Author": "Martin Thoma"})
    writer.add_named_destination("title", 0)
    writer.set_page_layout("/SinglePage")
    writer.page_mode = "/UseThumbs"

    output = BytesIO()
    writer.write(output)
    writer.close()
    return output


@apply_configuration(disable_legacy_handling=True)
def test_merge(benchmark):
    """Merge several documents, including an encrypted one, and add an outline."""
    output = benchmark(
        merge,
        (RESOURCE_ROOT / "crazyones.pdf").read_bytes(),
        (RESOURCE_ROOT / "pdflatex-outline.pdf").read_bytes(),
        (RESOURCE_ROOT / "pdflatex-forms.pdf").read_bytes(),
        (RESOURCE_ROOT / "libreoffice-writer-password.pdf").read_bytes(),
    )

    reader = PdfReader(output)
    assert [
        el.title for el in reader.outline if isinstance(el, Destination)
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


def text_extraction(data):
    reader = PdfReader(BytesIO(data))
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


@apply_configuration(disable_legacy_handling=True)
def test_text_extraction(benchmark):
    data = (SAMPLE_ROOT / "009-pdflatex-geotopo/GeoTopo.pdf").read_bytes()
    benchmark(text_extraction, data)


@apply_configuration(disable_legacy_handling=True)
def test_read_string_from_stream_performance(benchmark):
    """
    This test simulates reading an embedded base64 image of 256kb.
    It should be faster than a second, even on ancient machines.

    Runs < 100ms on a 2019 notebook. Takes 10 seconds prior to #1350.
    """
    data = b"(" + b"x" * 1024 * 256 + b")"
    assert benchmark(lambda: read_string_from_stream(BytesIO(data)))


def image_extraction(data):
    reader = PdfReader(BytesIO(data))
    return list(reader.pages[0].images)


@pytest.mark.enable_socket
@apply_configuration(disable_legacy_handling=True)
def test_image_new_property_performance(benchmark):
    """Extract many small images, some of them nested in form XObjects."""
    url = "https://github.com/py-pdf/pypdf/files/11219022/pdf_font_garbled.pdf"
    data = get_data_from_url(url=url, name="pdf_font_garbled.pdf")
    assert len(benchmark(image_extraction, data)) == 36


@pytest.mark.enable_socket
@apply_configuration(disable_legacy_handling=True)
def test_large_compressed_image_performance(benchmark):
    url = "https://github.com/py-pdf/pypdf/files/15306199/file_with_large_compressed_image.pdf"
    data = get_data_from_url(url=url, name="file_with_large_compressed_image.pdf")
    benchmark(image_extraction, data)
