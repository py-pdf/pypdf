"""Ensure that pypdf doesn't break PDF/A compliance."""

from io import BytesIO
from pathlib import Path
from typing import Optional

import pytest

from pypdf import PdfReader, PdfWriter


def is_pdfa1b_compliant(src: BytesIO):
    """Check if a PDF is PDF/A-1b compliant."""

    def document_information_has_analoguos_xml(src: BytesIO) -> bool:
        reader = PdfReader(src)
        meta = reader.metadata
        xmp = reader.xmp_metadata
        if not meta:
            return True
        if not xmp:
            return False
        if meta.title and not xmp.dc_title:
            return meta.title == xmp.dc_title
        return True

    return document_information_has_analoguos_xml(src)


@pytest.mark.samples
@pytest.mark.parametrize(
    ("src", "diagnostic_write_name"),
    [
        ("021-pdfa/crazyones-pdfa.pdf", None),
    ],
)
def test_pdfa(src: Path, diagnostic_write_name: Optional[str], sample_files_dir):
    with open(sample_files_dir / src, "rb") as fp:
        data = BytesIO(fp.read())
    reader = PdfReader(src)
    assert is_pdfa1b_compliant(data)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    stream = BytesIO()
    writer.write(stream)
    stream.seek(0)

    assert is_pdfa1b_compliant(stream)
    if diagnostic_write_name:
        with open(diagnostic_write_name, "wb") as fp:
            stream.seek(0)
            fp.write(stream.read())
