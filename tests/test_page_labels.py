"""Test the pypdf._page_labels module."""
from io import BytesIO

import pytest

from pypdf import PdfReader, PdfWriter
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
    TextStringObject,
)

from . import RESOURCE_ROOT, get_data_from_url


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
        (3_888, "MMMDCCCLXXXVIII"),
        (3_999, "MMMCMXCIX"),
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


@pytest.mark.parametrize("number", [0, -1, -5])
def test_number2roman_numeral_non_positive(number):
    """A non-positive number produced a numeral rather than being refused."""
    with pytest.raises(ValueError, match="Expecting a positive number"):
        number2uppercase_roman_numeral(number)
    with pytest.raises(ValueError, match="Expecting a positive number"):
        number2lowercase_roman_numeral(number)


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


def test_get_label_from_nums__truncated_pair(caplog):
    # Odd-length /Nums: the trailing key has no value object.
    value = DictionaryObject()
    value[NameObject("/S")] = NameObject("/D")
    dictionary_object = DictionaryObject()
    dictionary_object[NameObject("/Nums")] = ArrayObject(
        [NumberObject(0), value, NumberObject(5)]
    )
    assert get_label_from_nums(dictionary_object, 7) == "8"
    assert "Ignoring last /Nums key without a value." in caplog.text


def test_get_label_from_nums__unknown_style(caplog):
    # /S carries a numbering style that is not part of the specification.
    value = DictionaryObject()
    value[NameObject("/S")] = NameObject("/X")
    dictionary_object = DictionaryObject()
    dictionary_object[NameObject("/Nums")] = ArrayObject([NumberObject(0), value])
    assert get_label_from_nums(dictionary_object, 3) == "4"
    assert "Ignoring unknown page label numbering style '/X' in /Nums." in caplog.text


def test_get_label_from_nums__malformed_start(caplog):
    # /St is not an integer, so the label arithmetic cannot be performed.
    value = DictionaryObject()
    value[NameObject("/S")] = NameObject("/D")
    value[NameObject("/St")] = NameObject("/bad")
    dictionary_object = DictionaryObject()
    dictionary_object[NameObject("/Nums")] = ArrayObject([NumberObject(0), value])
    assert get_label_from_nums(dictionary_object, 3) == "4"
    assert caplog.messages == [
        (
            "Ignoring malformed page label entry in /Nums (/St='/bad', /P=''): "
            "unsupported operand type(s) for +: 'int' and 'NameObject'"
        )
    ]


def test_index2label__empty_kids_list():
    reader = PdfReader(RESOURCE_ROOT / "crazyones.pdf")
    number_tree = DictionaryObject()
    number_tree[NameObject("/Kids")] = ArrayObject()
    root = reader.root_object
    root[NameObject("/PageLabels")] = number_tree

    assert index2label(reader, 42) == "43"


@pytest.mark.parametrize(
    "limits",
    [
        None,  # /Limits key entirely absent
        ArrayObject([NumberObject(0)]),  # truncated to a single bound
    ],
)
def test_index2label__malformed_kid_limits(limits, caplog):
    reader = PdfReader(RESOURCE_ROOT / "crazyones.pdf")
    kid = DictionaryObject()
    if limits is not None:
        kid[NameObject("/Limits")] = limits
    kid[NameObject("/Nums")] = ArrayObject([NumberObject(0), DictionaryObject()])
    number_tree = DictionaryObject()
    number_tree[NameObject("/Kids")] = ArrayObject([kid])
    reader.root_object[NameObject("/PageLabels")] = number_tree

    assert index2label(reader, 5) == "6"
    assert "Ignoring kid with missing or malformed /Limits" in caplog.text
    assert "Could not reliably determine page label" in caplog.text


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(
            NumberObject(1), "Page labels are not a dictionary: 1", id="number"
        ),
        pytest.param(ArrayObject(), "Page labels are not a dictionary: []", id="array"),
        pytest.param(
            TextStringObject("x"), "Page labels are not a dictionary: x", id="string"
        ),
    ],
)
def test_index2label__page_labels_not_a_dictionary(caplog, value, expected):
    """A malformed /PageLabels raised a TypeError from the first membership test."""
    writer = PdfWriter()
    for _ in range(2):
        writer.add_blank_page(width=72, height=72)
    writer.root_object[NameObject("/PageLabels")] = value
    stream = BytesIO()
    writer.write(stream)
    stream.seek(0)

    assert PdfReader(stream).page_labels == ["1", "2"]
    assert expected in caplog.text


def test_get_label_from_nums__roman__limits(caplog):
    with pytest.raises(expected_exception=ValueError, match=r"^Number is out of range\.$"):
        number2uppercase_roman_numeral(4321)
    assert caplog.messages == []

    labels_large = DictionaryObject({
        NameObject("/Nums"): ArrayObject([
            NumberObject(0),
            DictionaryObject({
                NameObject("/S"): NameObject("/R"),
                NameObject("/St"): NumberObject(5000)
            })
        ])
    })
    assert get_label_from_nums(labels_large, 0) == "1"
    assert caplog.messages == [
        "Ignoring malformed page label entry in /Nums (/St=5000, /P=''): Number is out of range."
    ]

    labels_negative = DictionaryObject({
        NameObject("/Nums"): ArrayObject([
            NumberObject(-10_000),
            DictionaryObject({
                NameObject("/S"): NameObject("/R"),
            })
        ])
    })
    caplog.clear()
    assert get_label_from_nums(labels_negative, 0) == "1"
    assert caplog.messages == [
        "Ignoring malformed page label entry in /Nums (/St=1, /P=''): Number is out of range."
    ]
