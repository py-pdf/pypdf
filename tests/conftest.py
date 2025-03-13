"""Fixtures that are available automatically for all tests."""

import uuid
from pathlib import Path

import pytest

from pypdf import PdfReader

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


@pytest.fixture(scope="session")
def pdf_file_path(tmp_path_factory):
    return tmp_path_factory.mktemp("pypdf-data") / f"{uuid.uuid4()}.pdf"


@pytest.fixture(scope="session")
def txt_file_path(tmp_path_factory):
    return tmp_path_factory.mktemp("pypdf-data") / f"{uuid.uuid4()}.txt"


@pytest.fixture(scope="session")
def pdf_reader_page():
    """Gives a page that was retrieved from a PDF via PdfReader."""
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    return reader.pages[0]
