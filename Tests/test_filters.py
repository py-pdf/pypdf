from PyPDF2.filters import ASCIIHexDecode
import string
from PyPDF2.errors import PdfStreamError
import pytest


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
def test_expected_results(input, expected):
    """
    Feeds a bunch of values to ASCIIHexDecode.decode() and ensures the
    correct output is returned.
    TO-DO What is decode() supposed to do for such inputs as ">>", ">>>" or
    any other not terminated by ">"? (For the latter case, an exception
    is currently raised.)
    """

    assert ASCIIHexDecode.decode(input) == expected


def test_no_eod():
    """Ensuring an exception is raised when no EOD character is present"""
    with pytest.raises(PdfStreamError) as exc:
        ASCIIHexDecode.decode("")
    assert exc.value.args[0] == "Unexpected EOD in ASCIIHexDecode"
