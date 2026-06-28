"""Tests for pypdf.merge_pdfs."""

import sys
from unittest.mock import patch

import pytest

from pypdf import PdfReader
from pypdf.merge_pdfs import main, merge_pdfs

from . import RESOURCE_ROOT


def test_merge_pdfs_combines_page_counts(tmp_path):
    """Merged output contains all pages from both inputs in order."""
    first = RESOURCE_ROOT / "toy.pdf"
    second = RESOURCE_ROOT / "hello-world.pdf"
    output = tmp_path / "merged.pdf"

    merge_pdfs(first, second, output)

    merged = PdfReader(output)
    assert len(merged.pages) == len(PdfReader(first).pages) + len(PdfReader(second).pages)
    assert output.is_file()


def test_main_writes_merged_pdf(tmp_path):
    """CLI entry point merges two PDFs to the requested output path."""
    first = RESOURCE_ROOT / "toy.pdf"
    second = RESOURCE_ROOT / "hello-world.pdf"
    output = tmp_path / "cli-merged.pdf"
    argv = [
        "merge_pdfs",
        str(first),
        str(second),
        "-o",
        str(output),
    ]

    with patch.object(sys, "argv", argv):
        main()

    assert output.is_file()
    assert len(PdfReader(output).pages) == 2


def test_main_missing_input_file_exits_with_error():
    """CLI reports missing inputs before attempting a merge."""
    argv = [
        "merge_pdfs",
        "does-not-exist.pdf",
        str(RESOURCE_ROOT / "toy.pdf"),
        "-o",
        "out.pdf",
    ]

    with patch.object(sys, "argv", argv), pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 2
