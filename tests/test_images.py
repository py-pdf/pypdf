"""
Tests which ensure that image extraction works properly go here.

Typically, tests in here should compare the extracted images count, names,
and/or the actual image data with the expected value.
"""

from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from pypdf import PdfReader
from pypdf._page import PageObject

from . import get_pdf_from_url

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
SAMPLE_ROOT = PROJECT_ROOT / "sample-files"


def image_similarity(path1: Path, path2: Path) -> float:
    """
    Check image similarity.

    A value of "0" means the images are different. A value of 1 means they are
    identical. A value above 0.9 means they are almost the same
    """
    # Open the images using Pillow
    image1 = Image.open(path1)
    image2 = Image.open(path2)

    # Check if the images have the same dimensions
    if image1.size != image2.size:
        return 0

    # Check if the color modes are the same
    if image1.mode != image2.mode:
        return 0

    # Convert images to pixel data arrays
    pixels1 = list(image1.getdata())
    pixels2 = list(image2.getdata())
    # Calculate the Mean Squared Error (MSE)
    if isinstance(pixels1[0], tuple):
        mse = sum(
            sum((c1 - c2) ** 2 for c1, c2 in zip(p1, p2))
            for p1, p2 in zip(pixels1, pixels2)
        ) / len(pixels1)
    else:
        mse = sum((p1 - p2) ** 2 for p1, p2 in zip(pixels1, pixels2)) / len(pixels1)

    return 1 - mse


@pytest.mark.enable_socket()
def test_image_new_property():
    url = "https://github.com/py-pdf/pypdf/files/11219022/pdf_font_garbled.pdf"
    name = "pdf_font_garbled.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
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


@pytest.mark.parametrize(
    ("src", "page_index", "image_key", "expected"),
    [
        (
            SAMPLE_ROOT / "009-pdflatex-geotopo/GeoTopo.pdf",
            23,
            "/Im2",
            SAMPLE_ROOT / "009-pdflatex-geotopo/page-23-Im2.png",
        ),
        (
            SAMPLE_ROOT / "003-pdflatex-image/pdflatex-image.pdf",
            0,
            "/Im1",
            SAMPLE_ROOT / "003-pdflatex-image/page-0-Im1.jpg",
        ),
        (
            SAMPLE_ROOT / "018-base64-image/base64image.pdf",
            0,
            "/QuickPDFImd32aa1ab",
            SAMPLE_ROOT / "018-base64-image/page-0-QuickPDFImd32aa1ab.png",
        ),
        (
            SAMPLE_ROOT / "019-grayscale-image/grayscale-image.pdf",
            0,
            "/X0",
            SAMPLE_ROOT / "019-grayscale-image/page-0-X0.png",
        ),
    ],
    ids=[
        "009-pdflatex-geotopo/page-23-Im2.png",
        "003-pdflatex-image/page-0-Im1.jpg",
        "018-base64-image/page-0-QuickPDFImd32aa1ab.png",
        "019-grayscale-image/page-0-X0.png",
    ],
)
@pytest.mark.samples()
def test_image_extraction(src, page_index, image_key, expected):
    reader = PdfReader(src)
    actual_image = reader.pages[page_index].images[image_key]
    if not expected.exists():
        # A little helper for test generation
        with open(f"page-{page_index}-{actual_image.name}", "wb") as fp:
            fp.write(actual_image.data)
    assert image_similarity(BytesIO(actual_image.data), expected) >= 0.99
