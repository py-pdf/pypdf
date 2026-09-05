"""Tests for IndirectObject stream parsing security and DoS hardening."""

from io import BytesIO

import pytest

from pypdf._utils import read_until_whitespace
from pypdf.errors import PdfReadError
from pypdf.generic import IndirectObject
from pypdf.generic._base import ByteStringObject, TextStringObject
from pypdf.generic._utils import create_string_object, read_hex_string_from_stream


def test_indirect_object_valid():
    stream = BytesIO(b"12 0 R")
    obj = IndirectObject.read_from_stream(stream, None)
    assert obj.idnum == 12
    assert obj.generation == 0


def test_indirect_object_multiple_spaces():
    stream = BytesIO(b"42    7   R")
    obj = IndirectObject.read_from_stream(stream, None)
    assert obj.idnum == 42
    assert obj.generation == 7


def test_indirect_object_length_limit_idnum():
    # Long sequence of digits exceeding _LENGTH_LIMIT
    data = b"9" * 100
    stream = BytesIO(data)
    with pytest.raises(PdfReadError) as exc:
        IndirectObject.read_from_stream(stream, None)
    assert "exceeds maximum length limit" in str(exc.value)


def test_indirect_object_length_limit_generation():
    data = b"12 " + b"9" * 100
    stream = BytesIO(data)
    with pytest.raises(PdfReadError) as exc:
        IndirectObject.read_from_stream(stream, None)
    assert "exceeds maximum length limit" in str(exc.value)


@pytest.mark.timeout(2)
def test_indirect_object_dos_resistance():
    # 1,000,000 bytes input without spaces must be rejected in < 1s
    data = b"1" * 1_000_000
    stream = BytesIO(data)
    with pytest.raises(PdfReadError):
        IndirectObject.read_from_stream(stream, None)


def test_indirect_object_malformed_token():
    stream = BytesIO(b"abc 0 R")
    with pytest.raises(PdfReadError) as exc:
        IndirectObject.read_from_stream(stream, None)
    assert "Invalid indirect object reference" in str(exc.value)


def test_indirect_object_wrong_trailer():
    stream = BytesIO(b"12 0 obj")
    with pytest.raises(PdfReadError) as exc:
        IndirectObject.read_from_stream(stream, None)
    assert "Error reading indirect object reference" in str(exc.value)


def test_read_until_whitespace_with_null_byte():
    # PDF specification treats NUL (\x00) as whitespace
    stream = BytesIO(b"abc\x00def")
    result = read_until_whitespace(stream)
    assert result == b"abc"


def test_read_hex_string_and_create_string_object():
    stream = BytesIO(b"<48656c6c6f>")
    res = read_hex_string_from_stream(stream)
    assert isinstance(res, (TextStringObject, ByteStringObject))
    assert res == "Hello"

    # Test create_string_object with forced_encoding mapping
    mapping = {ord("A"): "Alpha", ord("B"): "Beta"}
    obj = create_string_object(b"AB", forced_encoding=mapping)
    assert obj == "AlphaBeta"
