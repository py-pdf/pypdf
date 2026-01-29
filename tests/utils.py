"""Utility functions and classes for testing."""
import logging
from typing import Union

from PIL import Image

from pypdf import PageObject
from pypdf.generic import DictionaryObject, IndirectObject


class PositionedText:
    """
    Specify a text with coordinates, font-dictionary and font-size.

    The font-dictionary may be None in case of an unknown font.
    """

    def __init__(self, text, x, y, font_dict, font_size) -> None:
        # TODO: \0-replace: Encoding issue in some files?
        self.text = text.replace("\0", "")
        self.x = x
        self.y = y
        self.font_dict = font_dict
        self.font_size = font_size

    def get_base_font(self) -> str:
        """
        Gets the base font of the text.

        Return UNKNOWN in case of an unknown font.
        """
        if (self.font_dict is None) or "/BaseFont" not in self.font_dict:
            return "UNKNOWN"
        return self.font_dict["/BaseFont"]


class Rectangle:
    """Specify a rectangle."""

    def __init__(self, x, y, w, h) -> None:
        self.x = x.as_numeric()
        self.y = y.as_numeric()
        self.w = w.as_numeric()
        self.h = h.as_numeric()

    def contains(self, x, y) -> bool:
        return (
                self.x <= x <= (self.x + self.w)
                and self.y <= y <= (self.y + self.h)
        )


def extract_text_and_rectangles(
        page: PageObject, rect_filter=None
) -> tuple[list[PositionedText], list[Rectangle]]:
    """
    Extracts texts and rectangles of a page of type pypdf._page.PageObject.

    This function supports simple coordinate transformations only.
    The optional rect_filter-lambda can be used to filter wanted
    rectangles.
    rect_filter has Rectangle as argument and must return a boolean.

    It returns a tuple containing a list of extracted texts and
    a list of extracted rectangles.
    """
    logger = logging.getLogger("extract_text_and_rectangles")

    rectangles = []
    texts = []

    def print_op_b(op, args, cm_matrix, tm_matrix) -> None:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"before: {op} at {cm_matrix}, {tm_matrix}")
        if op == b"re":
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"  add rectangle: {args}")
            w = args[2]
            h = args[3]
            r = Rectangle(args[0], args[1], w, h)
            if (rect_filter is None) or rect_filter(r):
                rectangles.append(r)

    def print_visi(text, cm_matrix, tm_matrix, font_dict, font_size) -> None:
        if text.strip() != "":
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"at {cm_matrix}, {tm_matrix}, font size={font_size}")
            texts.append(
                PositionedText(
                    text, tm_matrix[4], tm_matrix[5], font_dict, font_size
                )
            )

    visitor_before = print_op_b
    visitor_text = print_visi

    page.extract_text(
        visitor_operand_before=visitor_before, visitor_text=visitor_text
    )

    return texts, rectangles


def extract_table(
        texts: list[PositionedText], rectangles: list[Rectangle]
) -> list[list[list[PositionedText]]]:
    """
    Extracts a table containing text.

    It is expected that each cell is marked by a rectangle-object.
    It is expected that the page contains one table only.
    It is expected that the table contains at least 3 columns and 2 rows.

    A list of rows is returned.
    Each row contains a list of cells.
    Each cell contains a list of PositionedText-elements.
    """
    logger = logging.getLogger("extractTable")

    # Step 1: Count number of x- and y-coordinates of rectangles.
    # Remove duplicate rectangles. The new list is rectangles_filtered.
    col2count = {}
    row2count = {}
    key2rectangle = {}
    rectangles_filtered = []
    for r in rectangles:
        # Coordinates may be inaccurate, we have to round.
        # cell: x=72.264, y=386.57, w=93.96, h=46.584
        # cell: x=72.271, y=386.56, w=93.96, h=46.59
        key = f"{round(r.x, 0)} {round(r.y, 0)} {round(r.w, 0)} {round(r.h, 0)}"
        if key in key2rectangle:
            # Ignore duplicate rectangles
            continue
        key2rectangle[key] = r
        if r.x not in col2count:
            col2count[r.x] = 0
        if r.y not in row2count:
            row2count[r.y] = 0
        col2count[r.x] += 1
        row2count[r.y] += 1
        rectangles_filtered.append(r)

    # Step 2: Look for texts in rectangles.
    rectangle2texts = {}
    for text in texts:
        for r in rectangles_filtered:
            if r.contains(text.x, text.y):
                if r not in rectangle2texts:
                    rectangle2texts[r] = []
                rectangle2texts[r].append(text)
                break

    # PDF: y = 0 is expected at the bottom of the page.
    # So the header-row is expected to have the highest y-value.
    rectangles.sort(key=lambda r: (-r.y, r.x))

    # Step 3: Build the list of rows containing list of cell-texts.
    rows = []
    row_nr = 0
    col_nr = 0
    curr_y = None
    curr_row = None
    for r in rectangles_filtered:
        if col2count[r.x] < 3 or row2count[r.y] < 2:
            # We expect at least 3 columns and 2 rows.
            continue
        if curr_y is None or r.y != curr_y:
            # next row
            curr_y = r.y
            col_nr = 0
            row_nr += 1
            curr_row = []
            rows.append(curr_row)
        col_nr += 1
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"cell: x={r.x}, y={r.y}, w={r.w}, h={r.h}")
        if r not in rectangle2texts:
            curr_row.append("")
            continue
        cell_texts = list(rectangle2texts[r])
        curr_row.append(cell_texts)

    return rows


def extract_cell_text(cell_texts: list[PositionedText]) -> str:
    """Joins the text-objects of a cell."""
    return ("".join(t.text for t in cell_texts)).strip()


def get_image_data(
        image: Image.Image, band: Union[int, None] = None
) -> Union[tuple[tuple[int, ...], ...], tuple[float, ...]]:
    try:
        return image.get_flattened_data(band=band)
    except AttributeError:
        # For Pillow < 12.1.0
        return tuple(image.getdata(band=band))


class ReaderDummy:
    def __init__(self, strict=False) -> None:
        self.strict = strict

    def get_object(self, indirect_reference):
        class DummyObj:
            def get_object(self) -> "DummyObj":
                return self

        return DictionaryObject()

    def get_reference(self, obj):
        return IndirectObject(idnum=1, generation=1, pdf=self)
