"""Test the pypdf._xobj_image_helpers module."""
from io import BytesIO

import pytest

from pypdf import PdfReader
from pypdf._xobj_image_helpers import _extended_image_frombytes, _handle_flate
from pypdf.errors import EmptyImageDataError, PdfReadError
from pypdf.generic import ArrayObject, DecodedStreamObject, NameObject, NumberObject

from . import get_data_from_url


@pytest.mark.enable_socket
def test_get_imagemode_recursion_depth():
    """Avoid infinite recursion for nested color spaces."""
    url = "https://github.com/py-pdf/pypdf/files/12814018/out1.pdf"
    name = "issue2240.pdf"
    # Simple example: Just let the color space object reference itself.
    # The alternative would be to generate a chain of referencing objects.
    content = get_data_from_url(url, name=name)
    source = b"\n10 0 obj\n[ /DeviceN [ /HKS#2044#20K /Magenta /Yellow /Black ] 7 0 R 11 0 R 12 0 R ]\nendobj\n"
    target = b"\n10 0 obj\n[ /DeviceN [ /HKS#2044#20K /Magenta /Yellow /Black ] 10 0 R 11 0 R 12 0 R ]\nendobj\n"
    reader = PdfReader(BytesIO(content.replace(source, target)))
    with pytest.raises(
        PdfReadError,
        match="Color spaces nested too deeply. If required, consider increasing MAX_IMAGE_MODE_NESTING_DEPTH.",
    ):
        reader.pages[0].images[0]


def test_handle_flate__image_mode_1(caplog):
    data = b"\x00\xe0\x00"
    lookup = DecodedStreamObject()
    expected_data = [
        (66, 66, 66),
        (66, 66, 66),
        (66, 66, 66),
        (0, 19, 55),
        (0, 19, 55),
        (0, 19, 55),
        (66, 66, 66),
        (66, 66, 66),
        (66, 66, 66),
    ]

    # No trailing data.
    lookup.set_data(b"\x42\x42\x42\x00\x13\x37")
    result = _handle_flate(
        size=(3, 3),
        data=data,
        mode="1",
        color_space=ArrayObject(
            [NameObject("/Indexed"), NameObject("/DeviceRGB"), NumberObject(1), lookup]
        ),
        colors=2,
        obj_as_text="dummy",
    )
    assert expected_data == list(result[0].getdata())
    assert not caplog.text

    # Trailing whitespace.
    lookup.set_data(b"\x42\x42\x42\x00\x13\x37  \x0a")
    result = _handle_flate(
        size=(3, 3),
        data=data,
        mode="1",
        color_space=ArrayObject(
            [NameObject("/Indexed"), NameObject("/DeviceRGB"), NumberObject(1), lookup]
        ),
        colors=2,
        obj_as_text="dummy",
    )
    assert expected_data == list(result[0].getdata())
    assert not caplog.text

    # Trailing non-whitespace character.
    lookup.set_data(b"\x42\x42\x42\x00\x13\x37\x12")
    result = _handle_flate(
        size=(3, 3),
        data=data,
        mode="1",
        color_space=ArrayObject(
            [
                NameObject("/Indexed"),
                NameObject("/DeviceRGB"),
                NumberObject(1),
                lookup,
            ]
        ),
        colors=2,
        obj_as_text="dummy",
    )
    assert expected_data == list(result[0].getdata())
    assert "Too many lookup values: Expected 6, got 7." in caplog.text

    # Not enough lookup data.
    # `\xe0` of the original input (the middle part) does not use `0x37 = 55` for the lookup
    # here, but received a custom padding of `0`.
    lookup.set_data(b"\x42\x42\x42\x00\x13")
    caplog.clear()
    expected_short_data = [entry if entry[0] == 66 else (0, 19, 0) for entry in expected_data]
    result = _handle_flate(
        size=(3, 3),
        data=data,
        mode="1",
        color_space=ArrayObject(
            [
                NameObject("/Indexed"),
                NameObject("/DeviceRGB"),
                NumberObject(1),
                lookup,
            ]
        ),
        colors=2,
        obj_as_text="dummy",
    )
    assert expected_short_data == list(result[0].getdata())
    assert "Not enough lookup values: Expected 6, got 5." in caplog.text


def test_extended_image_frombytes_zero_data():
    mode = "RGB"
    size = (1, 1)
    data = b""

    with pytest.raises(EmptyImageDataError, match="Data is 0 bytes, cannot process an image from empty data."):
        _extended_image_frombytes(mode, size, data)
