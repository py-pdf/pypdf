# -*- coding: utf-8 -*-
import string
from itertools import product as cartesian_product

import pytest

from PyPDF2.errors import PdfReadError, PdfStreamError
from PyPDF2.filters import (
    ASCII85Decode,
    ASCIIHexDecode,
    CCITParameters,
    CCITTFaxDecode,
    FlateDecode,
)
from PyPDF2.generic import ArrayObject, DictionaryObject, NumberObject

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


@pytest.mark.parametrize(
    ("predictor", "s"), list(cartesian_product([1], filter_inputs))
)
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
    ("input", "expected"),
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
@pytest.mark.no_py27()
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


@pytest.mark.xfail()
def test_ASCII85Decode_with_overflow():
    inputs = (
        v + "~>"
        for v in "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0e\x0f"
        "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a"
        "\x1b\x1c\x1d\x1e\x1fvwxy{|}~\x7f\x80\x81\x82"
        "\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d"
        "\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98"
        "\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0¡¢£¤¥¦§¨©ª«¬"
        "\xad®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇ"
    )

    for i in inputs:
        with pytest.raises(ValueError) as exc:
            ASCII85Decode.decode(i)
        assert exc.value.args[0] == ""


@pytest.mark.no_py27()
def test_ASCII85Decode_five_zero_bytes():
    """
    From ISO 32000 (2008) §7.4.3:
    «As a special case, if all five bytes are 0, they shall be represented
    by the character with code 122 (z) instead of by five exclamation
    points (!!!!!).»
    """
    inputs = ("z", "zz", "zzz")
    exp_outputs = (
        b"\x00\x00\x00\x00",
        b"\x00\x00\x00\x00" * 2,
        b"\x00\x00\x00\x00" * 3,
    )

    assert ASCII85Decode.decode("!!!!!") == ASCII85Decode.decode("z")

    for expected, i in zip(exp_outputs, inputs):
        assert ASCII85Decode.decode(i) == expected


def test_CCITParameters():
    parms = CCITParameters()
    assert parms.K == 0  # zero is the default according to page 78
    assert parms.group == 3


@pytest.mark.parametrize(
    ("parameters", "expected_k"),
    [
        (None, 0),
        (ArrayObject([{"/K": 1}, {"/Columns": 13}]), 1),
    ],
)
def test_CCIT_get_parameters(parameters, expected_k):
    parmeters = CCITTFaxDecode._get_parameters(parameters=parameters, rows=0)
    assert parmeters.K == expected_k


def test_CCITTFaxDecode():
    data = b""
    parameters = DictionaryObject(
        {"/K": NumberObject(-1), "/Columns": NumberObject(17)}
    )

    # This was just the result PyPDF2 1.27.9 returned.
    # It would be awesome if we could check if that is actually correct.
    assert CCITTFaxDecode.decode(data, parameters) == (
        b"II*\x00\x08\x00\x00\x00\x08\x00\x00\x01\x04\x00\x01\x00\x00\x00\x11\x00"
        b"\x00\x00\x01\x01\x04\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x01"
        b"\x03\x00\x01\x00\x00\x00\x01\x00\x00\x00\x03\x01\x03\x00\x01\x00"
        b"\x00\x00\x04\x00\x00\x00\x06\x01\x03\x00\x01\x00\x00\x00\x00\x00"
        b"\x00\x00\x11\x01\x04\x00\x01\x00\x00\x00l\x00\x00\x00\x16\x01"
        b"\x04\x00\x01\x00\x00\x00\x00\x00\x00\x00\x17\x01\x04\x00\x01\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
    )
