"""Fixtures that are available automatically for all tests."""

import uuid

import pytest


@pytest.fixture(scope="session")
def pdf_file_path(tmp_path_factory):
    fn = tmp_path_factory.mktemp("pypdf-data") / f"{uuid.uuid4()}.pdf"
    return fn
