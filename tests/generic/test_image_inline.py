"""Test the pypdf.generic._image_inline module."""
from io import BytesIO

from pypdf.generic._image_inline import is_followed_by_binary_data


def test_is_followed_by_binary_data():
    # Empty/too short stream.
    stream = BytesIO()
    assert not is_followed_by_binary_data(stream)

    stream = BytesIO(b" q\n")
    assert not is_followed_by_binary_data(stream)

    # byte < 32 and no whitespace.
    stream = BytesIO(b"\x00\x11\x13\x37")
    assert is_followed_by_binary_data(stream)
    assert stream.read(1) == b"\x00"
    assert is_followed_by_binary_data(stream)
    assert stream.read(1) == b"\x11"
    assert is_followed_by_binary_data(stream)
    assert stream.read() == b"\x13\x37"

    # byte < 32, but whitespace.
    stream = BytesIO(b" q\n")
    assert not is_followed_by_binary_data(stream)

    # Whitespace only.
    stream = BytesIO(b" \n\n\n  \n")
    assert not is_followed_by_binary_data(stream)

    # No `operator_end`.
    stream = BytesIO(b"\n\n\n\n\n\n\n\nBT\n")
    assert not is_followed_by_binary_data(stream)

    # Operator length is <= 3.
    stream = BytesIO(b"\n\n\n\n\n\n\nBT\n")
    assert not is_followed_by_binary_data(stream)

    # Operator length is > 3.
    stream = BytesIO(b"\n\n\n\n\nTEST\n")
    assert is_followed_by_binary_data(stream)

    # Just characters.
    stream = BytesIO(b" ABCDEF")
    assert is_followed_by_binary_data(stream)

    # No `operator_start`.
    stream = BytesIO(b"ABCDEFG")
    assert is_followed_by_binary_data(stream)

    # Name object.
    stream = BytesIO(b"/R10 gs\n/R12 cs\n")
    assert not is_followed_by_binary_data(stream)

    # Numbers.
    stream = BytesIO(b"1337 42 m\n")
    assert not is_followed_by_binary_data(stream)

    stream = BytesIO(b"1234.56 42 13 37 10 20 c\n")
    assert not is_followed_by_binary_data(stream)
