"""Test the pypdf.annotations submodule."""

from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText, Text

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


def test_text_annotation(pdf_file_path):
    # Arrange
    pdf_path = RESOURCE_ROOT / "outline-without-title.pdf"
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)

    # Act
    text_annotation = Text(
        text="Hello World\nThis is the second line!",
        rect=(50, 550, 500, 650),
        open=True,
    )
    writer.add_annotation(0, text_annotation)

    # Assert: You need to inspect the file manually
    with open(pdf_file_path, "wb") as fp:
        writer.write(fp)


def test_free_text_annotation(pdf_file_path):
    # Arrange
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)

    # Act
    free_text_annotation = FreeText(
        text="Hello World - bold and italic\nThis is the second line!",
        rect=(50, 550, 200, 650),
        font="Arial",
        bold=True,
        italic=True,
        font_size="20pt",
        font_color="00ff00",
        border_color=None,
        background_color=None,
    )
    writer.add_annotation(0, free_text_annotation)

    free_text_annotation = FreeText(
        text="Another free text annotation (not bold, not italic)",
        rect=(500, 550, 200, 650),
        font="Arial",
        bold=False,
        italic=False,
        font_size="20pt",
        font_color="00ff00",
        border_color="0000ff",
        background_color="cdcdcd",
    )
    writer.add_annotation(0, free_text_annotation)

    # Assert: You need to inspect the file manually
    with open(pdf_file_path, "wb") as fp:
        writer.write(fp)
