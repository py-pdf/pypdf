"""Unit tests for the pypdf CLI program."""

import os
import sys
from pathlib import Path
from subprocess import check_output

try:
    from contextlib import chdir
except ImportError:  # Fallback when not available (< Python 3.11):
    from contextlib import contextmanager

    @contextmanager
    def chdir(dir_path):
        """Non thread-safe context manager to change the current working directory."""
        cwd = Path.cwd()
        os.chdir(dir_path)
        try:
            yield
        finally:
            os.chdir(cwd)


import pytest

from pypdf import PdfReader, __version__
from pypdf.__main__ import main

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


def test_pypdf_cli_can_be_invoked_as_a_module():
    stdout = check_output(
        [sys.executable, "-m", "pypdf", "--help"]  # noqa: S603
    ).decode()
    assert "usage: pypdf [-h]" in stdout


def test_pypdf_cli_version(capsys):
    main(["--version"])
    captured = capsys.readouterr()
    assert not captured.err
    assert __version__ in captured.out


def test_cat_incorrect_number_of_args(capsys, tmp_path):
    with pytest.raises(SystemExit), chdir(tmp_path):
        main(["cat", str(RESOURCE_ROOT / "box.pdf")])
    captured = capsys.readouterr()
    assert (
        "error: At least two PDF documents must be provided to the cat command"
        in captured.err
    )


def test_cat_ok(capsys, tmp_path):
    with chdir(tmp_path):
        main(
            [
                "cat",
                str(RESOURCE_ROOT / "box.pdf"),
                str(RESOURCE_ROOT / "jpeg.pdf"),
                "out.pdf",
            ]
        )
        reader = PdfReader("out.pdf")
        assert len(reader.pages) == 2
    captured = capsys.readouterr()
    assert not captured.err


def test_extract_images_jpg_png(capsys, tmp_path):
    with chdir(tmp_path):
        main(
            [
                "extract-images",
                str(RESOURCE_ROOT / "GeoBase_NHNC1_Data_Model_UML_EN.pdf"),
            ]
        )
    captured = capsys.readouterr()
    assert not captured.err
    assert captured.out.strip().split("\n") == [
        "Image extracted to Image7.jpg",
        "Image extracted to Image21.png",
        "Image extracted to Image81.png",
    ]


@pytest.mark.xfail()  # There is currently a bug there
def test_extract_images_monochrome(capsys, tmp_path):
    with chdir(tmp_path):
        main(["extract-images", str(RESOURCE_ROOT / "box.pdf")])
    captured = capsys.readouterr()
    assert not captured.err
    assert "Image extracted" in captured.out


def test_subset_ok(capsys, tmp_path):
    with chdir(tmp_path):
        main(
            [
                "subset",
                str(RESOURCE_ROOT / "GeoBase_NHNC1_Data_Model_UML_EN.pdf"),
                "1",
                "4",
                "14-16",
            ]
        )
        reader = PdfReader("subset.GeoBase_NHNC1_Data_Model_UML_EN.pdf")
        assert len(reader.pages) == 5
    captured = capsys.readouterr()
    assert not captured.err


@pytest.mark.parametrize(
    "page_range",
    ["", "a", "-", "-1", "1-", "1-1-1"],
)
def test_subset_invalid_args(capsys, tmp_path, page_range):
    with pytest.raises(SystemExit), chdir(tmp_path):
        main(["subset", str(RESOURCE_ROOT / "jpeg.pdf"), page_range])
    captured = capsys.readouterr()
    assert "error: Invalid page" in captured.err


def test_subset_warn_on_missing_pages(capsys, tmp_path):
    with chdir(tmp_path):
        main(["subset", str(RESOURCE_ROOT / "jpeg.pdf"), "2"])
    captured = capsys.readouterr()
    assert "WARN" in captured.out
