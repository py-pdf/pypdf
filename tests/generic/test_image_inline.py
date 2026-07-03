"""Test the pypdf.generic._image_inline module."""
from io import BytesIO

import pytest

from pypdf import PdfReader
from pypdf.errors import PdfReadError
from pypdf.generic._image_inline import (
    extract_inline__ascii85_decode,
    extract_inline__ascii_hex_decode,
    is_followed_by_binary_data,
)
from tests import get_data_from_url


def test_is_followed_by_binary_data() -> None:
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


@pytest.mark.enable_socket
def test_extract_inline_dct__early_end_of_file() -> None:
    url = "https://github.com/user-attachments/files/23056988/inline_dct__early_eof.pdf"
    name = "inline_dct__early_eof.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))
    page = reader.pages[0]

    with pytest.raises(
        expected_exception=PdfReadError, match=r"^Unexpected end of stream\.$"
    ):
        image = page.images[0].image
        assert image is not None
        image.load()


@pytest.mark.enable_socket
def test_extract_inline_dct__multiple_eod() -> None:
    url = "https://github.com/user-attachments/files/23900687/cedolini_esempio-1.pdf"
    name = "issue3517.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))

    for page in reader.pages:
        for image in page.images:
            assert image.image is not None
            _ = image.image.load()


@pytest.mark.timeout(5)
def test_extract_inline__ascii_hex_decode__early_end_of_file() -> None:
    stream = BytesIO(b"ABCDE\nF G")

    with pytest.raises(expected_exception=PdfReadError, match=r"^Unexpected end of stream\.$"):
        extract_inline__ascii_hex_decode(stream)


@pytest.mark.timeout(5)
def test_extract_inline__ascii85_decode__early_end_of_file() -> None:
    # Broken content stream, for example due to filter errors.
    # Specific example:
    #   Error -3 while decompressing data: invalid distance too far back
    #   b'[...] \nBI\n/W 16 /H 16 /BPC 8 /CS /RGB /F [/A85 /Fl]\nID\nGar8O(o6*i%*56~\ne  L\ne  L9/ LL9/ L'
    stream = BytesIO(b"Gar8O(o6*i%*56~\ne  L\ne  L9/ LL9/ L")

    with pytest.raises(expected_exception=PdfReadError, match=r"^Unexpected end of stream\.$"):
        extract_inline__ascii85_decode(stream)
