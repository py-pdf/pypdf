"""Fixtures that are available automatically for all tests."""

import uuid
from pathlib import Path

import pytest

from pypdf import PdfReader
from pypdf._page import PageObject

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent


@pytest.fixture(scope="session")
def pdf_file_path(tmp_path_factory):
    return tmp_path_factory.mktemp("pypdf-data") / f"{uuid.uuid4()}.pdf"


@pytest.fixture(scope="session")
def txt_file_path(tmp_path_factory):
    return tmp_path_factory.mktemp("pypdf-data") / f"{uuid.uuid4()}.txt"


# Reusable PDF fixtures
@pytest.fixture
def crazyones_pdf_page_one(crazyones_pdf_reader) -> PageObject:
    return crazyones_pdf_reader.pages[0]


@pytest.fixture
def crazyones_pdf_path(resources_dir) -> Path:
    return resources_dir / "crazyones.pdf"


@pytest.fixture
def crazyones_pdf_reader(crazyones_pdf_path) -> PdfReader:
    return PdfReader(crazyones_pdf_path)


@pytest.fixture
def project_dir() -> Path:
    return PROJECT_ROOT


@pytest.fixture
def resources_dir(project_dir) -> Path:
    return project_dir / "resources"


@pytest.fixture
def sample_files_dir(project_dir) -> Path:
    return project_dir / "resources"
