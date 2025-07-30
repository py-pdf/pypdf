"""Test the pypdf.papersizes module."""
import pytest

from pypdf import papersizes


def test_din_a0_paper_size():
    """The dimensions and area of the DIN A0 paper size are correct."""
    dim = papersizes.PaperSize.A0
    area_square_pixels = float(dim.width) * dim.height

    # 72 pixels is 1 inch
    area_square_inch = area_square_pixels / 72**2

    # 25.4 millimeter is equal to 1 inches
    area_square_mm = area_square_inch * (25.4) ** 2
    assert abs(area_square_mm - 999949) < 100
    conversion_factor = 72 / 25.4
    assert (dim.width - 841 * conversion_factor) < 1
    assert (dim.width - 1189 * conversion_factor) < 1


@pytest.mark.parametrize("dimensions", papersizes._din_a)
def test_din_a_aspect_ratio(dimensions):
    """The aspect ratio of DIN A paper sizes is correct."""
    assert abs(dimensions.height - dimensions.width * 2**0.5) <= 2.5


@pytest.mark.parametrize(
    ("dimensions_a", "dimensions_b"),
    list(zip(papersizes._din_a, papersizes._din_a[1:])),
)
def test_din_a_size_doubling(dimensions_a, dimensions_b):
    """The height of a DIN A paper size doubles when moving to the next size."""
    assert abs(dimensions_a.height - 2 * dimensions_b.width) <= 4
