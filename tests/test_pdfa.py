"""Check selected PDF/A metadata during document cloning."""

from io import BytesIO
from pathlib import Path
from typing import Optional

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.xmp import XmpInformation
from tests import SAMPLE_ROOT


def info_title_matches_xmp(src: BytesIO) -> bool:
    """Check /Info Title against XMP dc:title; this is not PDF/A validation."""
    reader = PdfReader(src)
    meta = reader.metadata
    if not meta or not meta.title:
        return True
    xmp = reader.xmp_metadata
    if not xmp or not xmp.dc_title:
        return False
    return meta.title in xmp.dc_title.values()


@pytest.mark.parametrize(
    ("info_title", "xmp_title", "expected"),
    [
        ("Same title", "Same title", True),
        ("Info title", "Different XMP title", False),
        ("Info title", None, False),
    ],
)
def test_info_title_matches_xmp(info_title: str, xmp_title: Optional[str], expected: bool) -> None:
    """Check matching and mismatched titles without claiming PDF/A compliance."""
    writer = PdfWriter()
    writer.add_blank_page(72, 72)
    writer.add_metadata({"/Title": info_title})
    xmp = XmpInformation.create()
    if xmp_title is not None:
        xmp.dc_title = {"x-default": xmp_title}
    writer.xmp_metadata = xmp
    stream = BytesIO()
    writer.write(stream)
    assert info_title_matches_xmp(stream) is expected


@pytest.mark.samples
@pytest.mark.parametrize(
    ("src", "diagnostic_write_name"),
    [
        (SAMPLE_ROOT / "021-pdfa/crazyones-pdfa.pdf", None),
    ],
)
def test_pdfa_title_metadata_preserved(src: Path, diagnostic_write_name: Optional[str]) -> None:
    """Regression for #1012: cloning should retain matching /Info and XMP titles."""
    with open(src, "rb") as fp:
        data = BytesIO(fp.read())
    reader = PdfReader(src)
    assert info_title_matches_xmp(data)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    stream = BytesIO()
    writer.write(stream)
    stream.seek(0)

    assert info_title_matches_xmp(stream)
    if diagnostic_write_name:
        with open(diagnostic_write_name, "wb") as fp:
            stream.seek(0)
            fp.write(stream.read())
