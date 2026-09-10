"""Test the pypdf._writer module."""

from pypdf import PdfReader, PdfWriter
from tests import RESOURCE_ROOT, SAMPLE_ROOT


def test_ocg():
    # Trying to get OCGs to append while preserving the OCGs in the original document
    reader = PdfReader(RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf")
    writer = PdfWriter()
    # writer.append(reader)
    writer.clone_document_from_reader(reader)
    reader_append = PdfReader(SAMPLE_ROOT / "029-optional-content-groups/ocg_map_test.pdf")

    # Trigger the append with the modified merge code that include the OCGs
    writer.append(reader_append)

    # 2. Add or change metadata values
    # Note: Keys must start with a forward slash (/)
    writer.add_metadata({
        "/Author": "Test Author",
        "/Producer": "Test Producer",
        "/Title": "Test Title",
        "/Subject": "Test Subject",
        "/Keywords": "Test Keywords",
        "/Creator": "Test Creator",
        "/CustomField": "Test CustomField",
    })

    writer.write(RESOURCE_ROOT / "output-ocg_map_test-1.pdf")

def test_ocg_2():
    # Trying to get OCGs to append while preserving the OCGs in the original document
    reader = PdfReader(SAMPLE_ROOT / "029-optional-content-groups/ocg_map_test.pdf")
    writer = PdfWriter()
    # writer.append(reader)
    writer.clone_document_from_reader(reader)
    reader_append = PdfReader(RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf")

    # Trigger the append with the modified merge code that include the OCGs
    writer.append(reader_append)

    writer.write(RESOURCE_ROOT / "output-ocg_map_test-2.pdf")
