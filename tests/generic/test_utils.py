"""Test the pypdf.generic._utils module."""
from pypdf.generic import create_string_object


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
