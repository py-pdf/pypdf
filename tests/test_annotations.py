"""Test the pypdf.annotations submodule."""

from io import BytesIO
from pathlib import Path

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.annotations import (
    AnnotationDictionary,
    Ellipse,
    FreeText,
    Highlight,
    Line,
    Link,
    Polygon,
    PolyLine,
    Popup,
    Rectangle,
    Text,
)
from pypdf.errors import DeprecationError, PdfReadError
from pypdf.generic import ArrayObject, FloatObject, NumberObject

from . import get_data_from_url

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


def test_ellipse(pdf_file_path):
    # Arrange
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)

    # Act
    with pytest.raises(DeprecationError):
        ellipse_annotation = Ellipse(
            rect=(50, 550, 500, 650),
            interiour_color="ff0000",
        )

    ellipse_annotation = Ellipse(
        rect=(50, 550, 500, 650),
        interior_color="ff0000",
    )
    writer.add_annotation(0, ellipse_annotation)

    # Assert: You need to inspect the file manually
    with open(pdf_file_path, "wb") as fp:
        writer.write(fp)


def test_text(pdf_file_path):
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


def test_free_text(pdf_file_path):
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


def test_free_text__font_specifier():
    free_text_annotation = FreeText(
        text="Hello World",
        rect=(0, 0, 0, 0),
    )
    assert free_text_annotation["/DS"] == "font: normal normal 14pt Helvetica;text-align:left;color:#000000"
    free_text_annotation = FreeText(
        text="Hello World",
        rect=(50, 550, 200, 650),
        font="Arial",
        bold=True,
        italic=True,
        font_size="20pt",
        font_color="00ff00",
        border_color=None,
        background_color=None,
    )
    assert free_text_annotation["/DS"] == "font: italic bold 20pt Arial;text-align:left;color:#00ff00"


def test_annotation_dictionary():
    a = AnnotationDictionary()
    a.flags = 123
    assert a.flags == 123


def test_polygon(pdf_file_path):
    # Arrange
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)

    with pytest.raises(ValueError):
        Polygon(
            vertices=[],
        )

    annotation = Polygon(
        vertices=[(50, 550), (200, 650), (70, 750), (50, 700)],
    )
    writer.add_annotation(0, annotation)

    # Assert: You need to inspect the file manually
    with open(pdf_file_path, "wb") as fp:
        writer.write(fp)


def test_polyline(pdf_file_path):
    # Arrange
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)

    with pytest.raises(ValueError):
        PolyLine(
            vertices=[],
        )

    annotation = PolyLine(
        vertices=[(50, 550), (200, 650), (70, 750), (50, 700)],
    )
    writer.add_annotation(0, annotation)

    # Assert: You need to inspect the file manually
    with open(pdf_file_path, "wb") as fp:
        writer.write(fp)


def test_line(pdf_file_path):
    # Arrange
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)

    # Act
    line_annotation = Line(
        text="Hello World\nLine2",
        rect=(50, 550, 200, 650),
        p1=(50, 550),
        p2=(200, 650),
    )
    writer.add_annotation(0, line_annotation)

    # Assert: You need to inspect the file manually
    with open(pdf_file_path, "wb") as fp:
        writer.write(fp)


def test_rectangle(pdf_file_path):
    # Arrange
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)

    # Act
    with pytest.raises(DeprecationError):
        square_annotation = Rectangle(
            rect=(50, 550, 200, 650), interiour_color="ff0000"
        )

    square_annotation = Rectangle(
        rect=(50, 550, 200, 650), interior_color="ff0000"
    )
    writer.add_annotation(0, square_annotation)

    square_annotation = Rectangle(rect=(40, 400, 150, 450))
    writer.add_annotation(0, square_annotation)

    # Assert: You need to inspect the file manually
    with open(pdf_file_path, "wb") as fp:
        writer.write(fp)


def test_highlight(pdf_file_path):
    # Arrange
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)

    # Act
    highlight_annotation = Highlight(
        rect=(95.79332, 704.31777, 138.55779, 724.6855),
        highlight_color="ff0000",
        quad_points=ArrayObject(
            [
                FloatObject(100.060779),
                FloatObject(723.55398),
                FloatObject(134.29033),
                FloatObject(723.55398),
                FloatObject(100.060779),
                FloatObject(705.4493),
                FloatObject(134.29033),
                FloatObject(705.4493),
            ]
        ),
        printing=False,
    )
    writer.add_annotation(0, highlight_annotation)
    for annot in writer.pages[0]["/Annots"]:
        obj = annot.get_object()
        subtype = obj["/Subtype"]
        if subtype == "/Highlight":
            assert "/F" not in obj or obj["/F"] == NumberObject(0)

    writer.add_page(page)
    # Act
    highlight_annotation = Highlight(
        rect=(95.79332, 704.31777, 138.55779, 724.6855),
        highlight_color="ff0000",
        quad_points=ArrayObject(
            [
                FloatObject(100.060779),
                FloatObject(723.55398),
                FloatObject(134.29033),
                FloatObject(723.55398),
                FloatObject(100.060779),
                FloatObject(705.4493),
                FloatObject(134.29033),
                FloatObject(705.4493),
            ]
        ),
        printing=True,
    )
    writer.add_annotation(1, highlight_annotation)
    for annot in writer.pages[1]["/Annots"]:
        obj = annot.get_object()
        subtype = obj["/Subtype"]
        if subtype == "/Highlight":
            assert obj["/F"] == NumberObject(4)

    # Assert: You need to inspect the file manually
    with open(pdf_file_path, "wb") as fp:
        writer.write(fp)


def test_link(pdf_file_path):
    # Arrange
    pdf_path = RESOURCE_ROOT / "outline-without-title.pdf"
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)

    # Act
    # Part 1: Too many args
    with pytest.raises(ValueError):
        Link(
            rect=(50, 550, 200, 650),
            url="https://martin-thoma.com/",
            target_page_index=3,
        )

    # Part 2: Too few args
    with pytest.raises(ValueError):
        Link(
            rect=(50, 550, 200, 650),
        )

    # Part 3: External Link
    link_annotation = Link(
        rect=(50, 50, 100, 100),
        url="https://martin-thoma.com/",
        border=[1, 0, 6, [3, 2]],
    )
    writer.add_annotation(0, link_annotation)

    # Part 4: Internal Link
    link_annotation = Link(
        rect=(100, 100, 300, 200),
        target_page_index=1,
        border=[50, 10, 4],
    )
    writer.add_annotation(0, link_annotation)

    for page in reader.pages[1:]:
        writer.add_page(page)

    # Assert: You need to inspect the file manually
    with open(pdf_file_path, "wb") as fp:
        writer.write(fp)


def test_popup(caplog):
    # Arrange
    pdf_path = RESOURCE_ROOT / "outline-without-title.pdf"
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)

    # Act
    text_annotation = Text(
        title_bar="hello world",
        text="Hello World\nThis is the second line!",
        rect=(50, 550, 200, 650),
        open=True,
    )
    ta = writer.add_annotation(0, text_annotation)
    popup_annotation = Popup(
        rect=(50, 550, 200, 650),
        open=True,
        parent=ta,  # prefer to use for evolutivity
    )
    writer.add_annotation(writer.pages[0], popup_annotation)

    Popup(
        rect=(50, 550, 200, 650),
        open=True,
        parent=True,  # broken parameter  # type: ignore
    )
    assert "Unregistered Parent object : No Parent field set" in caplog.text

    target = "annotated-pdf-popup.pdf"
    writer.write(target)
    Path(target).unlink()  # comment this out for manual inspection


@pytest.mark.enable_socket
def test_outline_action_without_d_lenient():
    reader = PdfReader(BytesIO(get_data_from_url(name="iss3268.pdf")))
    assert len(reader.outline) == 2


@pytest.mark.enable_socket
def test_outline_action_without_d_strict(pdf_file_path):
    reader = PdfReader(BytesIO(get_data_from_url(name="iss3268.pdf")))
    reader.strict = True
    with pytest.raises(PdfReadError) as e:
        assert len(reader.outline) == 2
    assert "Outline Action Missing /D" in str(e)
