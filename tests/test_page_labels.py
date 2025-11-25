"""Test the pypdf._page_labels module."""
from io import BytesIO
from pathlib import Path

import pytest

from pypdf import PdfReader
from pypdf._page_labels import (
    get_label_from_nums,
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
    ArrayObject,
    DictionaryObject,
    NameObject,
    NullObject,
    NumberObject,
)

from . import get_data_from_url

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


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


@pytest.mark.enable_socket
def test_index2label(caplog):
    name = "waarom-meisjes-het-beter-doen-op-HAVO-en-VWO-ROA.pdf"
    r = PdfReader(BytesIO(get_data_from_url(name=name)))
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


@pytest.mark.enable_socket
def test_index2label_kids():
    url = "https://github.com/py-pdf/pypdf/files/14858124/Terminologie_Epochen.Schwerpunkte.Umsetzungen.pdf"
    r = PdfReader(BytesIO(get_data_from_url(url=url, name="index2label_kids.pdf")))
    expected = [
        "C1",
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
        "IX",
        "X",
        "XI",
        "XII",
        "XIII",
        "XIV",
        "XV",
        "XVI",
        "XVII",
        *list(map(str, range(1, 284)))
    ]
    for x in ["20", "44", "58", "82", "94", "116", "154", "166", "192", "224", "250"]:
        # Some page labels are unused. Removing them is still easier than copying the
        # whole list itself here.
        expected.remove(x)
    assert r.page_labels == expected


@pytest.mark.enable_socket
def test_index2label_kids__recursive(caplog):
    url = "https://github.com/py-pdf/pypdf/files/14842446/tt1.pdf"
    r = PdfReader(
        BytesIO(get_data_from_url(url=url, name="index2label_kids_recursive.pdf"))
    )
    expected = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "17",
        "18",
        "19",
    ]
    assert r.page_labels == expected
    assert caplog.text != ""


def test_get_label_from_nums__empty_nums_list():
    dictionary_object = DictionaryObject()
    dictionary_object[NameObject("/Nums")] = ArrayObject()
    assert get_label_from_nums(dictionary_object, 13) == "14"


def test_index2label__empty_kids_list():
    reader = PdfReader(RESOURCE_ROOT / "crazyones.pdf")
    number_tree = DictionaryObject()
    number_tree[NameObject("/Kids")] = ArrayObject()
    root = reader.root_object
    root[NameObject("/PageLabels")] = number_tree

    assert index2label(reader, 42) == "43"
