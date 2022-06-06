import io
import os

import pytest

import PyPDF2._utils
from PyPDF2._utils import (
    mark_location,
    matrix_multiply,
    read_until_regex,
    read_until_whitespace,
    skip_over_comment,
    skip_over_whitespace,
)
from PyPDF2.errors import PdfStreamError

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "resources")


@pytest.mark.parametrize(
    ("stream", "expected"),
    [
        (io.BytesIO(b"foo"), False),
        (io.BytesIO(b""), False),
        (io.BytesIO(b" "), True),
        (io.BytesIO(b"  "), True),
        (io.BytesIO(b"  \n"), True),
        (io.BytesIO(b"    \n"), True),
    ],
)
def test_skip_over_whitespace(stream, expected):
    assert skip_over_whitespace(stream) == expected


def test_read_until_whitespace():
    assert read_until_whitespace(io.BytesIO(b"foo"), maxchars=1) == b"f"


@pytest.mark.parametrize(
    ("stream", "remainder"),
    [
        (io.BytesIO(b"% foobar\n"), b""),
        (io.BytesIO(b""), b""),
        (io.BytesIO(b" "), b" "),
        (io.BytesIO(b"% foo%\nbar"), b"bar"),
    ],
)
def test_skip_over_comment(stream, remainder):
    skip_over_comment(stream)
    assert stream.read() == remainder


def test_read_until_regex_premature_ending_raise():
    import re

    stream = io.BytesIO(b"")
    with pytest.raises(PdfStreamError) as exc:
        read_until_regex(stream, re.compile(b"."))
    assert exc.value.args[0] == "Stream has ended unexpectedly"


def test_read_until_regex_premature_ending_name():
    import re

    stream = io.BytesIO(b"")
    assert read_until_regex(stream, re.compile(b"."), ignore_eof=True) == b""


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (((3,),), ((7,),), ((21,),)),
        (((3, 7),), ((5,), (13,)), ((3 * 5.0 + 7 * 13,),)),
        (((3,), (7,)), ((5, 13),), ((3 * 5, 3 * 13), (7 * 5, 7 * 13))),
    ],
)
def test_matrix_multiply(a, b, expected):
    assert matrix_multiply(a, b) == expected


def test_mark_location():
    stream = io.BytesIO(b"abde" * 6000)
    mark_location(stream)
    os.remove("PyPDF2_pdfLocation.txt")  # cleanup


def test_hex_str():
    assert PyPDF2._utils.hex_str(10) == "0xa"


def test_b():
    assert PyPDF2._utils.b_("foo") == b"foo"
    assert PyPDF2._utils.b_("😀") == "😀".encode()
    assert PyPDF2._utils.b_("‰") == "‰".encode()
    assert PyPDF2._utils.b_("▷") == "▷".encode()


def test_deprecate_no_replacement():
    with pytest.raises(PendingDeprecationWarning) as exc:
        PyPDF2._utils.deprecate_no_replacement("foo")
    error_msg = "foo is deprecated and will be removed in PyPDF2 3.0.0."
    assert exc.value.args[0] == error_msg
