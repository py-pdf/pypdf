"""Test the pypdf.generic._image_inline module."""
from base64 import a85encode
from io import BytesIO
from typing import Callable

import pytest

from pypdf import PdfReader
from pypdf.errors import PdfReadError
from pypdf.generic._image_inline import (
    BUFFER_SIZE,
    _check_end_image_marker,
    extract_inline__ascii85_decode,
    extract_inline__ascii_hex_decode,
    extract_inline__dct_decode,
    extract_inline__run_length_decode,
    extract_inline_default,
    is_followed_by_binary_data,
)
from tests import get_data_from_url


@pytest.mark.parametrize("tail", [b"", b"\n", b" ", b"\r", b"\t", b"\f", b"\x00", b"\nQ\n"])
def test_check_end_image_marker_at_end_of_stream(tail: bytes) -> None:
    """An accepted marker leaves the stream at `E`, including at EOF."""
    stream = BytesIO(b"image\nEI" + tail)
    stream.seek(len(b"image"))

    assert _check_end_image_marker(stream)
    assert stream.tell() == len(b"image\n")
    assert stream.read(2) == b"EI"


@pytest.mark.parametrize("tail", [b"", b"\n", b"\nQ\n"])
@pytest.mark.parametrize(
    ("extractor", "image_data"),
    [
        (extract_inline__ascii_hex_decode, b"41>"),
        (extract_inline__ascii85_decode, a85encode(b"A") + b"~>"),
        (extract_inline__run_length_decode, b"\x00A\x80"),
        # JPEG start/end markers suffice to exercise the extractor's cursor contract.
        (extract_inline__dct_decode, b"\xff\xd8\xff\xd9"),
    ],
    ids=["ASCIIHex", "ASCII85", "RunLength", "DCT"],
)
def test_extract_filtered_inline_image_at_end_of_stream(
    extractor: Callable[[BytesIO], bytes], image_data: bytes, tail: bytes
) -> None:
    """Filtered extraction returns exact data and leaves the stream at `EI`."""
    stream = BytesIO(image_data + b"\nEI" + tail)

    assert extractor(stream) == image_data
    assert stream.tell() == len(image_data) + 1
    assert stream.read() == b"EI" + tail


@pytest.mark.parametrize("marker", [b"", b"\nE", b"\nEX", b"\nEIX"])
@pytest.mark.parametrize(
    ("extractor", "image_data"),
    [
        (extract_inline__ascii_hex_decode, b"41>"),
        (extract_inline__ascii85_decode, a85encode(b"A") + b"~>"),
        (extract_inline__run_length_decode, b"\x00A\x80"),
        (extract_inline__dct_decode, b"\xff\xd8\xff\xd9"),
    ],
    ids=["ASCIIHex", "ASCII85", "RunLength", "DCT"],
)
def test_extract_filtered_inline_image_rejects_invalid_marker(
    extractor: Callable[[BytesIO], bytes], image_data: bytes, marker: bytes
) -> None:
    """Missing, incomplete and undelimited markers retain the existing error."""
    with pytest.raises(PdfReadError, match=r"^EI stream not found\.$"):
        extractor(BytesIO(image_data + marker))


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


@pytest.mark.parametrize("following_operator", [b"E", b"Q"])
def test_extract_inline_default_ignores_unbounded_ei(following_operator: bytes) -> None:
    image_data = b"pixels\x0bEI\x00\x09" + following_operator * 2 + b"\x00\x08more-pixels\n"
    stream = BytesIO(image_data + b"EI\nQ")

    assert extract_inline_default(stream) == image_data
    assert stream.read(2) == b"EI"


def test_extract_inline_default_ignores_ei_without_closing_operator() -> None:
    """An `EI` without leading delimiter is no end marker if no closing operator follows."""
    image_data = b"pixels\x0bEI\nBT\n"
    stream = BytesIO(image_data + b"EI\nQ")

    assert extract_inline_default(stream) == image_data
    assert stream.read(2) == b"EI"


@pytest.mark.parametrize("following_operator", [b"Q", b"EMC"])
def test_extract_inline_default_empty_image_data(following_operator: bytes) -> None:
    """The `EI` marker has no leading delimiter at all if the image data is empty."""
    stream = BytesIO(b"EI\n" + following_operator + b"\nBT\n")

    assert extract_inline_default(stream) == b""
    assert stream.read(2) == b"EI"


def test_extract_inline_default_finds_ei_across_buffer_boundary() -> None:
    image_data = b"A" * (BUFFER_SIZE - 1) + b"\n"
    stream = BytesIO(image_data + b"EI\nQ")

    assert extract_inline_default(stream) == image_data
    assert stream.read(2) == b"EI"


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
