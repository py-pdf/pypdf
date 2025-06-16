"""Ensure that pypdf doesn't break PDF/A compliance."""

from io import BytesIO
from pathlib import Path
from typing import Optional

import pytest

from pypdf import PdfReader, PdfWriter

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
SAMPLE_ROOT = PROJECT_ROOT / "sample-files"


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
        (SAMPLE_ROOT / "021-pdfa/crazyones-pdfa.pdf", None),
    ],
)
def test_pdfa(src: Path, diagnostic_write_name: Optional[str]):
    with open(src, "rb") as fp:
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


def test_pdfa_xmp_metadata():
    """Test PDF/A XMP metadata access using available test files."""
    test_files = [
        "tests/pdf_cache/index2label_kids.pdf",
        "tests/pdf_cache/2021_book_security.pdf",
        "tests/pdf_cache/iss2290.pdf",
        "tests/pdf_cache/embedded_files_kids.pdf"
    ]

    for pdf_path in test_files:
        file_path = Path(pdf_path)
        if file_path.exists():
            reader = PdfReader(file_path)
            xmp = reader.xmp_metadata

            if xmp is not None:
                part = xmp.pdfaid_part
                conformance = xmp.pdfaid_conformance
                combined = xmp.pdf_a_conformance

                if part is not None and conformance is not None:
                    assert isinstance(part, str)
                    assert isinstance(conformance, str)
                    assert combined == f"{part}{conformance}"

                    assert part in ["1", "2", "3"]
                    assert conformance in ["A", "B", "U"]
                elif part is not None or conformance is not None:
                    pass
                else:
                    assert combined is None





def test_pdfa_xmp_no_metadata():
    """Test XMP with no PDF/A metadata returns None values."""
    from pypdf.xmp import XmpInformation
    from pypdf.generic import ContentStream
    
    xmp_no_pdfa = """<?xml version="1.0" encoding="UTF-8"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
                     xmlns:dc="http://purl.org/dc/elements/1.1/">
      <dc:title>Test Document</dc:title>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>"""
    
    stream = ContentStream(None, None)
    stream.set_data(xmp_no_pdfa.encode())
    xmp_info = XmpInformation(stream)
    
    assert xmp_info.pdfaid_part is None
    assert xmp_info.pdfaid_conformance is None
    assert xmp_info.pdf_a_conformance is None


def test_pdfa_xmp_part_only():
    """Test XMP with only PDF/A part (no conformance) returns None for combined."""
    from pypdf.xmp import XmpInformation
    from pypdf.generic import ContentStream
    
    xmp_part_only = """<?xml version="1.0" encoding="UTF-8"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
                     xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">
      <pdfaid:part>2</pdfaid:part>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>"""
    
    stream = ContentStream(None, None)
    stream.set_data(xmp_part_only.encode())
    xmp_info = XmpInformation(stream)
    
    assert xmp_info.pdfaid_part == "2"
    assert xmp_info.pdfaid_conformance is None
    assert xmp_info.pdf_a_conformance is None


def test_pdfa_xmp_conformance_only():
    """Test XMP with only PDF/A conformance (no part) returns None for combined."""
    from pypdf.xmp import XmpInformation
    from pypdf.generic import ContentStream
    
    xmp_conformance_only = """<?xml version="1.0" encoding="UTF-8"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
                     xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">
      <pdfaid:conformance>A</pdfaid:conformance>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>"""
    
    stream = ContentStream(None, None)
    stream.set_data(xmp_conformance_only.encode())
    xmp_info = XmpInformation(stream)
    
    assert xmp_info.pdfaid_part is None
    assert xmp_info.pdfaid_conformance == "A"
    assert xmp_info.pdf_a_conformance is None


def test_pdfa_xmp_complete_metadata():
    """Test XMP with complete PDF/A metadata combines part and conformance."""
    from pypdf.xmp import XmpInformation
    from pypdf.generic import ContentStream
    
    xmp_complete = """<?xml version="1.0" encoding="UTF-8"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
                     xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">
      <pdfaid:part>3</pdfaid:part>
      <pdfaid:conformance>B</pdfaid:conformance>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>"""
    
    stream = ContentStream(None, None)
    stream.set_data(xmp_complete.encode())
    xmp_info = XmpInformation(stream)
    
    assert xmp_info.pdfaid_part == "3"
    assert xmp_info.pdfaid_conformance == "B"
    assert xmp_info.pdf_a_conformance == "3B"


def test_pdfa_xmp_attribute_style():
    """Test XMP with attribute-style PDF/A metadata (as mentioned in issue #3313)."""
    from pypdf.xmp import XmpInformation
    from pypdf.generic import ContentStream
    
    xmp_attribute_style = """<?xml version="1.0" encoding="UTF-8"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about="" 
                     xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/"
                     pdfaid:part="1" 
                     pdfaid:conformance="B" />
  </rdf:RDF>
</x:xmpmeta>"""
    
    stream = ContentStream(None, None)
    stream.set_data(xmp_attribute_style.encode())
    xmp_info = XmpInformation(stream)
    
    assert xmp_info.pdfaid_part == "1"
    assert xmp_info.pdfaid_conformance == "B"
    assert xmp_info.pdf_a_conformance == "1B"
