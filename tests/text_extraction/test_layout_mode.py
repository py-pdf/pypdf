"""Tests for layout mode extraction."""
import pytest

from pypdf import PdfReader
from tests.test_text_extraction import _page_with_helvetica


@pytest.mark.timeout(5)  # Before: 2 minutes
def test_add_tm__matrix_multiplications() -> None:
    n = 16_000
    content = b"BT /F1 12 Tf " + b"1 1 Td (x) Tj " * n + b"ET"
    data = _page_with_helvetica(content)

    reader = PdfReader(data)
    page = reader.pages[0]

    assert page.extract_text(extraction_mode="layout") == "x" * n


@pytest.mark.timeout(5)
def test_extra_operands_before_tm_are_tolerated() -> None:
    """Extra operands left on the stack before `Tm` must not overflow the transform (#4283).

    A matrix operator consumes the 6 operands nearest to it, so the layout output must
    match the equivalent stream carrying only those 6 operands.
    """
    extra = _page_with_helvetica(b"BT /F1 12 Tf 72 720 1 0 0 1 100 600 Tm (TmText) Tj ET")
    clean = _page_with_helvetica(b"BT /F1 12 Tf 1 0 0 1 100 600 Tm (TmText) Tj ET")

    assert PdfReader(extra).pages[0].extract_text(extraction_mode="layout") == PdfReader(
        clean
    ).pages[0].extract_text(extraction_mode="layout")


@pytest.mark.timeout(5)
def test_extra_operands_before_cm_are_tolerated() -> None:
    """Extra operands left on the stack before `cm` must not overflow the transform."""
    extra = _page_with_helvetica(
        b"BT /F1 12 Tf 5 5 1 0 0 1 100 600 cm 1 0 0 1 0 0 Tm (CmText) Tj ET"
    )
    clean = _page_with_helvetica(b"BT /F1 12 Tf 1 0 0 1 100 600 cm 1 0 0 1 0 0 Tm (CmText) Tj ET")

    assert PdfReader(extra).pages[0].extract_text(extraction_mode="layout") == PdfReader(
        clean
    ).pages[0].extract_text(extraction_mode="layout")
