"""Test the pypdf.generic._utils module."""
import pytest

from pypdf.generic import TextStringObject, create_string_object


def test_create_string_object__forced_encoding__list() -> None:
    forced_encoding = list(map(chr, range(250)))
    assert create_string_object(b"Hello World!\xff", forced_encoding=forced_encoding) == "Hello World!\xff"

    forced_encoding = list(map(chr, range(256)))
    forced_encoding[ord("A")] = "Hello"
    forced_encoding[ord("B")] = "World"
    assert create_string_object(b"A B!", forced_encoding=forced_encoding) == "Hello World!"


def test_create_string_object__forced_encoding__dict() -> None:
    forced_encoding = dict(zip(range(250), map(chr, range(250))))
    assert create_string_object(b"Hello World!", forced_encoding=forced_encoding) == "Hello World!"

    forced_encoding = {ord("A"): "Hello", ord("B"): "World"}
    assert create_string_object(b"A B!", forced_encoding=forced_encoding) == "Hello World!"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(b"\xef\xbb\xbf", "", id="bom-only"),
        pytest.param(b"\xef\xbb\xbfHello World", "Hello World", id="ascii"),
        pytest.param(b"\xef\xbb\xbfGr\xc3\xbc\xc3\x9fe \xe2\x82\xac", "Grüße €", id="latin-and-euro"),
        pytest.param(b"\xef\xbb\xbf\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e", "日本語", id="cjk"),
    ],
)
def test_create_string_object__utf8(value: bytes, expected: str) -> None:
    result = create_string_object(value)
    assert isinstance(result, TextStringObject)
    assert result == expected
    assert result.original_bytes == value
    assert result.get_encoded_bytes() == value


def test_create_string_object__utf8__invalid() -> None:
    # Not valid UTF-8 after the BOM, thus still decoded as PDFDocEncoding.
    result = create_string_object(b"\xef\xbb\xbf\xe9t\xe9")
    assert isinstance(result, TextStringObject)
    assert result == "\xef\xbb\xbf\xe9t\xe9"
    assert result.original_bytes == b"\xef\xbb\xbf\xe9t\xe9"
