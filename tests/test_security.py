"""Test the pypdf._security module."""
from pypdf._security import _alg32
from pypdf.generic import ByteStringObject


def test_alg32_metadata_encrypt():
    # I don't know how to ensure the value is actually the correct one
    assert (
        _alg32(
            "a",
            rev=3,
            keylen=3,
            owner_entry=ByteStringObject(b""),
            p_entry=0,
            id1_entry=ByteStringObject(b""),
            metadata_encrypt=True,
        )
        == b"S\xcfQ"
    )


def test_alg32_no_metadata_encrypt():
    # I don't know how to ensure the value is actually the correct one
    assert (
        _alg32(
            "a",
            rev=3,
            keylen=3,
            owner_entry=ByteStringObject(b""),
            p_entry=0,
            id1_entry=ByteStringObject(b""),
            metadata_encrypt=False,
        )
        == b"@wt"
    )
