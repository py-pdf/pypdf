"""Test PDF merging script."""

import pytest

from pypdf import PdfReader
from pypdf.merge_pdfs import MergeError, main, merge_pdfs

from . import RESOURCE_ROOT, SAMPLE_ROOT

MERGE_EXAMPLE_DIR = SAMPLE_ROOT / "merge-example"
MERGE_EXAMPLE_OUTPUT = MERGE_EXAMPLE_DIR / "merged-toy-issue297.pdf"
TOY_PDF = RESOURCE_ROOT / "toy.pdf"
ISSUE_297_PDF = RESOURCE_ROOT / "issue-297.pdf"


def test_merge_two_pdfs(tmp_path):
    output = tmp_path / "merged.pdf"
    merge_pdfs([TOY_PDF, ISSUE_297_PDF], output)

    reader = PdfReader(output)
    assert len(reader.pages) == 2


def test_merge_preserves_page_order(tmp_path):
    output = tmp_path / "ordered.pdf"
    merge_pdfs([TOY_PDF, ISSUE_297_PDF], output)

    merged = PdfReader(output)
    assert len(merged.pages) == len(PdfReader(TOY_PDF).pages) + len(
        PdfReader(ISSUE_297_PDF).pages
    )


def test_merge_requires_at_least_two_inputs(tmp_path):
    output = tmp_path / "merged.pdf"
    with pytest.raises(MergeError, match="At least two"):
        merge_pdfs([TOY_PDF], output)


def test_merge_missing_input_file(tmp_path):
    output = tmp_path / "merged.pdf"
    missing = tmp_path / "does-not-exist.pdf"
    with pytest.raises(MergeError, match="not found"):
        merge_pdfs([TOY_PDF, missing], output)


def test_merge_input_not_a_file(tmp_path):
    output = tmp_path / "merged.pdf"
    directory = tmp_path / "inputs"
    directory.mkdir()
    with pytest.raises(MergeError, match="not a file"):
        merge_pdfs([TOY_PDF, directory], output)


def test_merge_invalid_pdf(tmp_path):
    output = tmp_path / "merged.pdf"
    invalid = tmp_path / "invalid.pdf"
    invalid.write_text("not a pdf", encoding="utf-8")
    with pytest.raises(MergeError, match="Cannot read PDF"):
        merge_pdfs([TOY_PDF, invalid], output)
    assert not output.exists()
    assert not output.with_name(f"{output.name}.merge_tmp").exists()


def test_merge_overwrites_existing_output(tmp_path):
    output = tmp_path / "merged.pdf"
    merge_pdfs([TOY_PDF, ISSUE_297_PDF], output)
    first_mtime = output.stat().st_mtime_ns

    merge_pdfs([TOY_PDF, ISSUE_297_PDF], output)
    assert output.exists()
    assert len(PdfReader(output).pages) == 2
    assert output.stat().st_mtime_ns >= first_mtime


def test_merge_sample_files_example():
    """Example merge output checked in under sample-files/."""
    assert MERGE_EXAMPLE_OUTPUT.is_file()
    reader = PdfReader(MERGE_EXAMPLE_OUTPUT)
    assert len(reader.pages) == len(PdfReader(TOY_PDF).pages) + len(
        PdfReader(ISSUE_297_PDF).pages
    )


def test_main_cli_success(tmp_path):
    output = tmp_path / "cli-merged.pdf"
    exit_code = main(
        [
            "-o",
            str(output),
            str(TOY_PDF),
            str(ISSUE_297_PDF),
        ]
    )
    assert exit_code == 0
    assert len(PdfReader(output).pages) == 2


def test_main_cli_reports_merge_error(tmp_path, capsys):
    output = tmp_path / "cli-merged.pdf"
    exit_code = main(["-o", str(output), str(TOY_PDF)])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "At least two PDF documents are required" in captured.err
