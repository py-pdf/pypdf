"""Test the pypdf._xobj_image_helpers module."""
from io import BytesIO
from pathlib import Path

import pytest

from pypdf import PdfReader
from pypdf._xobj_image_helpers import _extended_image_frombytes, _handle_flate
from pypdf.errors import EmptyImageDataError, PdfReadError
from pypdf.generic import ArrayObject, DecodedStreamObject, NameObject, NumberObject

from . import get_data_from_url

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


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
        match=r"Color spaces nested too deeply\. If required, consider increasing MAX_IMAGE_MODE_NESTING_DEPTH\.",
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

    with pytest.raises(EmptyImageDataError, match=r"Data is 0 bytes, cannot process an image from empty data\."):
        _extended_image_frombytes(mode, size, data)


def test_handle_flate__autodesk_indexed():
    reader = PdfReader(RESOURCE_ROOT / "AutoCad_Diagram.pdf")
    page = reader.pages[0]
    for name, image in page.images.items():
        assert name.startswith("/")
        image.image.load()

    data = RESOURCE_ROOT.joinpath("AutoCad_Diagram.pdf").read_bytes()
    data = data.replace(b"/DeviceRGB\x00255", b"/DeviceRGB")
    reader = PdfReader(BytesIO(data))
    page = reader.pages[0]
    with pytest.raises(
            PdfReadError,
            match=r"^Expected color space with 4 values, got 3: \['/Indexed', '/DeviceRGB', '\\x00\\x80\\x00\\x80\\x80耀"  # noqa: E501
    ):
        for name, _image in page.images.items():  # noqa: PERF102
            assert name.startswith("/")


@pytest.mark.enable_socket
def test_get_mode_and_invert_color():
    url = "https://github.com/user-attachments/files/18381726/tika-957721.pdf"
    name = "tika-957721.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    page = reader.pages[12]
    for _name, image in page.images.items():  # noqa: PERF102
        image.image.load()


@pytest.mark.enable_socket
def test_get_imagemode__empty_array():
    url = "https://github.com/user-attachments/files/23050451/poc.pdf"
    name = "issue3499.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    page = reader.pages[0]

    with pytest.raises(expected_exception=PdfReadError, match=r"^ColorSpace field not found in .+"):
        page.images[0].image.load()
