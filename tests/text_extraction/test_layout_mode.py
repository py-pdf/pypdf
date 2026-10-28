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
