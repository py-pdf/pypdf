"""Test the pypdf._page_labels module."""
from io import BytesIO

import pytest

from pypdf import PdfReader
from pypdf._page_labels import (
    index2label,
    number2lowercase_letter,
    number2lowercase_roman_numeral,
    number2uppercase_letter,
    number2uppercase_roman_numeral,
    nums_clear_range,
    nums_insert,
    nums_next,
)
from pypdf.generic import (
    DictionaryObject,
    NameObject,
    NullObject,
    NumberObject,
)

from . import get_pdf_from_url


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (1, "I"),
        (2, "II"),
        (3, "III"),
        (4, "IV"),
        (5, "V"),
        (6, "VI"),
        (7, "VII"),
        (8, "VIII"),
        (9, "IX"),
        (10, "X"),
    ],
)
def test_number2uppercase_roman_numeral(number, expected):
    assert number2uppercase_roman_numeral(number) == expected


def test_number2lowercase_roman_numeral():
    assert number2lowercase_roman_numeral(123) == "cxxiii"


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (1, "a"),
        (2, "b"),
        (3, "c"),
        (25, "y"),
        (26, "z"),
        (27, "aa"),
        (28, "ab"),
    ],
)
def test_number2lowercase_letter(number, expected):
    assert number2lowercase_letter(number) == expected


def test_number2uppercase_letter():
    with pytest.raises(ValueError):
        number2uppercase_letter(-1)


@pytest.mark.external
def test_index2label(caplog):
    url = "https://github.com/py-pdf/pypdf/files/10773829/waarom-meisjes-het-beter-doen-op-HAVO-en-VWO-ROA.pdf"
    name = "waarom-meisjes-het-beter-doen-op-HAVO-en-VWO-ROA.pdf"
    r = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    assert index2label(r, 1) == "ii"
    assert index2label(r, 9) == "6"
    # very silly data to get test cover
    r.trailer["/Root"]["/PageLabels"]["/Nums"].append(8)
    r.trailer["/Root"]["/PageLabels"]["/Nums"].append(NullObject())
    assert index2label(r, 9) == "10"

    with pytest.raises(ValueError):
        nums_clear_range(
            NumberObject(10), 8, r.trailer["/Root"]["/PageLabels"]["/Nums"]
        )
    r.trailer["/Root"]["/PageLabels"]["/Nums"].append(8)
    with pytest.raises(ValueError):
        nums_next(NumberObject(10), r.trailer["/Root"]["/PageLabels"]["/Nums"])
    with pytest.raises(ValueError):
        nums_clear_range(
            NumberObject(10), 8, r.trailer["/Root"]["/PageLabels"]["/Nums"]
        )
    with pytest.raises(ValueError):
        nums_insert(
            NumberObject(10),
            DictionaryObject(),
            r.trailer["/Root"]["/PageLabels"]["/Nums"],
        )

    del r.trailer["/Root"]["/PageLabels"]["/Nums"]
    assert index2label(r, 1) == "2"
    caplog.clear()
    r.trailer["/Root"]["/PageLabels"][NameObject("/Kids")] = NullObject()
    assert index2label(r, 1) == "2"
    assert caplog.text != ""
