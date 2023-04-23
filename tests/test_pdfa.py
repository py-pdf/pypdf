"""Ensure that pypdf doesn't break PDF/A compliance."""

from io import BytesIO
from pathlib import Path

import pytest

from pypdf import PdfReader, PdfWriter

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
SAMPLE_ROOT = PROJECT_ROOT / "sample-files"


def is_pdfa1b_compliant(reader: PdfReader):
    """Check if a PDF is PDF/A-1b compliant."""

    def document_information_has_analoguos_xml(reader: PdfReader) -> bool:
        meta = reader.metadata
        xmp = reader.xmp_metadata
        if not meta:
            return True
        if not xmp:
            return False
        if meta.title and not xmp.dc_title:
            return False
        return True

    return document_information_has_analoguos_xml(reader)


@pytest.mark.xfail(reason="clone_document_from_reader seems to be broken")
@pytest.mark.parametrize(
    "src",
    [
        (SAMPLE_ROOT / "021-pdfa/crazyones-pdfa.pdf",),
    ],
)
def test_pdfa(src):
    reader = PdfReader(src)
    assert is_pdfa1b_compliant(reader)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    stream = BytesIO()
    writer.write(stream)
    stream.seek(0)

    out_reader = PdfReader(stream)
    assert is_pdfa1b_compliant(out_reader)
