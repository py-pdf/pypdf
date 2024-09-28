"""Test LZW-related code."""

import pytest

from pypdf.filters import LZWDecode
from pypdf.lzw import lzw_encode

test_cases = [
    pytest.param(b"", id="Empty input"),  # Empty input
    pytest.param(b"A", id="Single character"),
    pytest.param(b"AAAAAA", id="Repeating character"),
    pytest.param(b"Hello, World!", id="Simple text"),
    pytest.param(b"ABABABABABAB", id="Repeating pattern"),
    pytest.param(b"The quick brown fox jumps over the lazy dog", id="Longer text"),
    pytest.param(b"\x00\xFF\x00\xFF", id="Binary data"),
]


@pytest.mark.parametrize("data", test_cases)
def test_encode_decode(data):
    """Decoder and encoder match."""
    compressed_data = lzw_encode(data)
    decoded = LZWDecode._decodeb(compressed_data)
    assert decoded == data
