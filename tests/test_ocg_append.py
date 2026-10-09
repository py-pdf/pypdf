"""Test the pypdf._writer module."""

from pypdf import PdfReader, PdfWriter
from tests import RESOURCE_ROOT, SAMPLE_ROOT


def test_ocg_append_metadata_preservation(tmp_path):
    # Trying to get OCGs to append while preserving the OCGs in the original document
    writer = PdfWriter(clone_from=RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf")

    reader_append = PdfReader(SAMPLE_ROOT / "029-optional-content-groups/ocg_map_test.pdf")

    # 1. Trigger the append with the modified merge code that include the OCGs
    writer.append(reader_append)

    # 2. Add or change metadata values
    writer.add_metadata({
        "/Author": "Test Author",
        "/Producer": "Test Producer",
        "/Title": "Test Title",
        "/Subject": "Test Subject",
        "/Keywords": "Test Keywords",
        "/Creator": "Test Creator",
        "/CustomField": "Test CustomField",
    })

    writer.write(tmp_path / "output-ocg_append_metadata_preservation.pdf")

def test_ocg_append_metadata_reverse_order(tmp_path):
    # Testing the same scenario, but PDFs appended in reverse order
    writer = PdfWriter(clone_from=SAMPLE_ROOT / "029-optional-content-groups/ocg_map_test.pdf")

    reader_append = PdfReader(RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf")

    # 1.Trigger the append with the modified merge code that include the OCGs
    writer.append(reader_append)

    # 2. Add or change metadata values
    writer.add_metadata({
        "/Author": "Test Author",
        "/Producer": "Test Producer",
        "/Title": "Test Title",
        "/Subject": "Test Subject",
        "/Keywords": "Test Keywords",
        "/Creator": "Test Creator",
        "/CustomField": "Test CustomField",
    })

    writer.write(tmp_path / "output-ocg_append_metadata_reverse_order.pdf")

def test_ocg_insert_with_merge(tmp_path):
    # This test is meant to output a PDF that is comparable to the test_workflows.py
    # "test_merge_output" test of expected vs actual size. Though it might be different due to
    # the metadata being preserved.
    # Should be named "Seige_of_Vicksburg_Sample_OCR-crazyones-merged.pdf" in the Resource root
    # or https://github.com/py-pdf/pypdf/blob/main/resources/Seige_of_Vicksburg_Sample_OCR-crazyones-merged.pdf
    writer = PdfWriter(clone_from=RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf")

    reader_append = PdfReader(RESOURCE_ROOT / "crazyones.pdf")

    # Trigger the append with the modified merge code that include the OCGs
    writer.merge(1, reader_append)

    writer.write(tmp_path / "output-ocg_insert_with_merge.pdf")

def test_ocg_insert_with_merge_no_clone(tmp_path):
    # This test is meant to output a PDF that is comparable to the test_workflows.py output
    # but without the old metadata preserved by "clone_from" parameter and
    # results in a differing file size.
    # The difference between the following for
    # the test_workflows.py "test_merge_output" test:
    # cloning which preserves metadata: 220,005
    # no cloning, metadata not preserved: 217,997
    writer = PdfWriter()
    writer.append(RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf")

    reader_append = PdfReader(RESOURCE_ROOT / "crazyones.pdf")

    # Trigger the append with the modified merge code that include the OCGs
    writer.merge(1, reader_append)

    writer.write(tmp_path / "output-ocg_insert_with_merge_no_clone.pdf")
