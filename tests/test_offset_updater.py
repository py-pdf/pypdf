import pytest
from pathlib import Path

from PyPDF2.offset_updater import update_lines

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


def test_issue_297():
    pdf_path = RESOURCE_ROOT / "issue-297.pdf"
    encoding = "UTF-8"
    with open(pdf_path, "r") as f:
        linesOut = update_lines(f, encoding)

    # Generation of issue-297-xref.pdf:
    # python PyPDF2/offset_updater.py -v resources/issue-297.pdf resources/issue-297-xref.pdf
    #
    pdf_path_expected = RESOURCE_ROOT / "issue-297-xref.pdf"
    with open(pdf_path_expected, "r") as f:
        lineNo = 0
        itOut = linesOut.__iter__()
        for lineExp in f:
            lineNo += 1
            line = itOut.__next__()
            assert line == lineExp, f"difference in line {lineNo}"
