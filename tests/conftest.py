"""Fixtures that are available automatically for all tests."""

import uuid
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def pdf_file_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("pypdf-data") / f"{uuid.uuid4()}.pdf"


@pytest.fixture(scope="session")
def txt_file_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("pypdf-data") / f"{uuid.uuid4()}.txt"
