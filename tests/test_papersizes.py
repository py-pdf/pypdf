"""Test the pypdf.papersizes module."""
import pytest

from pypdf import papersizes


def test_din_a0_paper_size() -> None:
    """The dimensions and area of the DIN A0 paper size are correct."""
    dim = papersizes.PaperSize.A0
    area_square_pixels = float(dim.width) * dim.height

    # 72 pixels is 1 inch
    area_square_inch = area_square_pixels / 72**2

    # 25.4 millimeter is equal to 1 inches
    area_square_mm = area_square_inch * (25.4) ** 2
    assert abs(area_square_mm - 999949) < 100
    conversion_factor = 72 / 25.4
    assert abs(dim.width - 841 * conversion_factor) < 1
    assert abs(dim.height - 1189 * conversion_factor) < 1


@pytest.mark.parametrize("dimensions", papersizes._din_a)
def test_din_a_aspect_ratio(dimensions: papersizes.Dimensions) -> None:
    """The aspect ratio of DIN A paper sizes is correct."""
    assert abs(dimensions.height - dimensions.width * 2**0.5) <= 2.5


@pytest.mark.parametrize(
    ("dimensions_a", "dimensions_b"),
    list(zip(papersizes._din_a, papersizes._din_a[1:])),
)
def test_din_a_size_doubling(
    dimensions_a: papersizes.Dimensions, dimensions_b: papersizes.Dimensions
) -> None:
    """
    Each DIN A paper size is the next smaller size doubled.

    Halving A(n) across its height gives A(n+1), so the width of A(n) is the
    height of A(n+1) and the height of A(n) is about twice the width of A(n+1).
    """
    assert dimensions_a.width == dimensions_b.height
    assert abs(dimensions_a.height - 2 * dimensions_b.width) <= 4


def test_c4_envelope_paper_size() -> None:
    """
    The C4 envelope paper size is 229 mm x 324 mm.

    ISO 269 defines C4 as 229 mm x 324 mm, which is 649 x 918 at 72 ppi.
    """
    conversion_factor = 72 / 25.4
    dim = papersizes.PaperSize.C4
    assert abs(dim.width - 229 * conversion_factor) < 1
    assert abs(dim.height - 324 * conversion_factor) < 1
