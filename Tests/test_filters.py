import string
from itertools import product as cartesian_product

import pytest

from PyPDF2.errors import PdfReadError, PdfStreamError
from PyPDF2.filters import ASCIIHexDecode, FlateDecode

filter_inputs = (
    # "", '', """""",
    string.ascii_lowercase,
    string.ascii_uppercase,
    string.ascii_letters,
    string.digits,
    string.hexdigits,
    string.punctuation,
    string.whitespace,  # Add more...
)


@pytest.mark.parametrize("predictor, s", list(cartesian_product([1], filter_inputs)))
def test_FlateDecode(predictor, s):
    """
    Tests FlateDecode decode() and encode() methods.
    """
    codec = FlateDecode()
    s = s.encode()
    encoded = codec.encode(s)
    assert codec.decode(encoded, {"/Predictor": predictor}) == s


def test_FlateDecode_unsupported_predictor():
    """
    Inputs an unsupported predictor (outside the [10, 15] range) checking
    that PdfReadError() is raised. Once this predictor support is updated
    in the future, this test case may be removed.
    """
    codec = FlateDecode()
    predictors = (-10, -1, 0, 9, 16, 20, 100)

    for predictor, s in cartesian_product(predictors, filter_inputs):
        s = s.encode()
        with pytest.raises(PdfReadError):
            codec.decode(codec.encode(s), {"/Predictor": predictor})


@pytest.mark.parametrize(
    "input,expected",
    [
        (">", ""),
        (
            "6162636465666768696a6b6c6d6e6f707172737475767778797a>",
            string.ascii_lowercase,
        ),
        (
            "4142434445464748494a4b4c4d4e4f505152535455565758595a>",
            string.ascii_uppercase,
        ),
        (
            "6162636465666768696a6b6c6d6e6f707172737475767778797a4142434445464748494a4b4c4d4e4f505152535455565758595a>",
            string.ascii_letters,
        ),
        ("30313233343536373839>", string.digits),
        (
            "3  031323334353637   3839>",
            string.digits,
        ),  # Same as previous, but whitespaced
        ("30313233343536373839616263646566414243444546>", string.hexdigits),
        ("20090a0d0b0c>", string.whitespace),
    ],
    ids=[
        "empty",
        "ascii_lowercase",
        "ascii_uppercase",
        "ascii_letters",
        "digits",
        "digits_whitespace",
        "hexdigits",
        "whitespace",
    ],
)
@pytest.mark.no_py27
def test_ASCIIHexDecode(input, expected):
    """
    Feeds a bunch of values to ASCIIHexDecode.decode() and ensures the
    correct output is returned.
    TO-DO What is decode() supposed to do for such inputs as ">>", ">>>" or
    any other not terminated by ">"? (For the latter case, an exception
    is currently raised.)
    """

    assert ASCIIHexDecode.decode(input) == expected


def test_ASCIIHexDecode_no_eod():
    """Ensuring an exception is raised when no EOD character is present"""
    with pytest.raises(PdfStreamError) as exc:
        ASCIIHexDecode.decode("")
    assert exc.value.args[0] == "Unexpected EOD in ASCIIHexDecode"
