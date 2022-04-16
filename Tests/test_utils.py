import io
import os

import pytest

import PyPDF2.utils
from PyPDF2 import PdfFileReader
from PyPDF2.errors import PdfStreamError

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


@pytest.mark.parametrize(
    "value,expected", [(0, True), (-1, True), (1, True), ("1", False), (1.5, False)]
)
def test_isInt(value, expected):
    assert PyPDF2.utils.isInt(value) == expected


def test_isBytes():
    assert PyPDF2.utils.isBytes(b"")


@pytest.mark.parametrize(
    "stream,expected",
    [
        (io.BytesIO(b"foo"), False),
        (io.BytesIO(b""), False),
        (io.BytesIO(b" "), True),
        (io.BytesIO(b"  "), True),
        (io.BytesIO(b"  \n"), True),
        (io.BytesIO(b"    \n"), True),
    ],
)
def test_skipOverWhitespace(stream, expected):
    assert PyPDF2.utils.skipOverWhitespace(stream) == expected


def test_readUntilWhitespace():
    assert PyPDF2.utils.readUntilWhitespace(io.BytesIO(b"foo"), maxchars=1) == b"f"


@pytest.mark.parametrize(
    "stream,remainder",
    [
        (io.BytesIO(b"% foobar\n"), b""),
        (io.BytesIO(b""), b""),
        (io.BytesIO(b" "), b" "),
        (io.BytesIO(b"% foo%\nbar"), b"bar"),
    ],
)
def test_skipOverComment(stream, remainder):
    PyPDF2.utils.skipOverComment(stream)
    assert stream.read() == remainder


def test_readUntilRegex_premature_ending_raise():
    import re

    stream = io.BytesIO(b"")
    with pytest.raises(PdfStreamError) as exc:
        PyPDF2.utils.readUntilRegex(stream, re.compile(b"."))
    assert exc.value.args[0] == "Stream has ended unexpectedly"


def test_readUntilRegex_premature_ending_name():
    import re

    stream = io.BytesIO(b"")
    assert PyPDF2.utils.readUntilRegex(stream, re.compile(b"."), ignore_eof=True) == b""


@pytest.mark.parametrize(
    "a,b,expected",
    [
        ([[3]], [[7]], [[21]]),
        ([[3, 7]], [[5], [13]], [[3 * 5.0 + 7 * 13]]),
        ([[3], [7]], [[5, 13]], [[3 * 5, 3 * 13], [7 * 5, 7 * 13]]),
    ],
)
def test_matrixMultiply(a, b, expected):
    assert PyPDF2.utils.matrixMultiply(a, b) == expected


def test_markLocation():
    stream = io.BytesIO(b"abde" * 6000)
    PyPDF2.utils.markLocation(stream)
    os.remove("PyPDF2_pdfLocation.txt")  # cleanup


def test_ConvertFunctionsToVirtualList():
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    reader = PdfFileReader(pdf_path)

    # Test if getting as slice throws an error
    assert len(reader.pages[:]) == 1


def test_hexStr():
    assert PyPDF2.utils.hexStr(10) == "0xa"
