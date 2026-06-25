"""Test the pypdf.generic._image_xobject module."""
import zlib
from io import BytesIO

import PIL
import pytest
from PIL import Image

from pypdf import PdfReader
from pypdf._utils import Version
from pypdf.constants import ColorSpaces, FilterTypes, ImageAttributes, StreamAttributes
from pypdf.errors import EmptyImageDataError, LimitReachedError, PdfReadError
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    NameObject,
    NumberObject,
    PdfObject,
    StreamObject,
    TextStringObject,
)
from pypdf.generic._image_xobject import (
    _get_image_mode,
    _handle_flate,
    _image_from_bytes,
    _xobj_to_image,
    bits2byte,
)

from .. import RESOURCE_ROOT, get_data_from_url
from ..utils import get_image_data


def _handle_flate_indexed_image_mode_1(base: str, lookup_data: bytes) -> Image.Image:
    lookup = DecodedStreamObject()
    lookup.set_data(lookup_data)
    result = _handle_flate(
        size=(3, 3),
        data=b"\x00\xe0\x00",
        mode="1",
        color_space=ArrayObject(
            [NameObject("/Indexed"), NameObject(base), NumberObject(1), lookup]
        ),
        colors=2,
        obj_as_text="dummy",
    )
    return result[0]


@pytest.mark.enable_socket
def test_get_imagemode_recursion_depth() -> None:
    """Avoid infinite recursion for nested color spaces."""
    url = "https://github.com/py-pdf/pypdf/files/12814018/out1.pdf"
    name = "issue2240.pdf"
    # Simple example: Just let the color space object reference itself.
    # The alternative would be to generate a chain of referencing objects.
    content = get_data_from_url(url=url, name=name)
    source = b"\n10 0 obj\n[ /DeviceN [ /HKS#2044#20K /Magenta /Yellow /Black ] 7 0 R 11 0 R 12 0 R ]\nendobj\n"
    target = b"\n10 0 obj\n[ /DeviceN [ /HKS#2044#20K /Magenta /Yellow /Black ] 10 0 R 11 0 R 12 0 R ]\nendobj\n"
    reader = PdfReader(BytesIO(content.replace(source, target)))
    with pytest.raises(
        PdfReadError,
        match=r"Color spaces nested too deeply\. If required, consider increasing MAX_IMAGE_MODE_NESTING_DEPTH\.",
    ):
        reader.pages[0].images[0]


def test_handle_flate__image_mode_1(caplog: pytest.LogCaptureFixture) -> None:
    data = b"\x00\xe0\x00"
    lookup = DecodedStreamObject()
    expected_data = (
        (66, 66, 66),
        (66, 66, 66),
        (66, 66, 66),
        (0, 19, 55),
        (0, 19, 55),
        (0, 19, 55),
        (66, 66, 66),
        (66, 66, 66),
        (66, 66, 66),
    )

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
    assert expected_data == get_image_data(result[0])
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
    assert expected_data == get_image_data(result[0])
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
    assert expected_data == get_image_data(result[0])
    assert "Too many lookup values: Expected 6, got 7." in caplog.text

    # Not enough lookup data.
    # `\xe0` of the original input (the middle part) does not use `0x37 = 55` for the lookup
    # here, but received a custom padding of `0`.
    lookup.set_data(b"\x42\x42\x42\x00\x13")
    caplog.clear()
    expected_short_data = tuple([entry if entry[0] == 66 else (0, 19, 0) for entry in expected_data])
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
    assert expected_short_data == get_image_data(result[0])
    assert "Not enough lookup values: Expected 6, got 5." in caplog.text


@pytest.mark.parametrize(
    ("lookup_data", "expected_data"),
    [
        (b"\x00\xff", (0, 0, 0, 255, 255, 255, 0, 0, 0)),
        (b"\xff\x00", (255, 255, 255, 0, 0, 0, 255, 255, 255)),
    ],
)
def test_handle_flate__image_mode_1_device_gray_issue_3850(
        caplog: pytest.LogCaptureFixture,
        lookup_data: bytes,
        expected_data: tuple[int, ...],
) -> None:
    """
    1-bit /Indexed DeviceGray images are extracted with the lookup applied.

    This test is a regression test for issue #3850.
    """
    image = _handle_flate_indexed_image_mode_1("/DeviceGray", lookup_data)
    assert image.mode == "L"
    assert get_image_data(image) == expected_data
    assert not caplog.text


def test_handle_flate__image_mode_1_unsupported_base(caplog: pytest.LogCaptureFixture) -> None:
    """An unknown base resolves to a zero-byte lookup width: skip the lookup with a warning."""
    image = _handle_flate_indexed_image_mode_1("/SomethingUnknown", b"\x00\xff")
    assert image.mode == "RGB"
    assert get_image_data(image) == (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (255, 255, 255),
        (255, 255, 255),
        (255, 255, 255),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    )
    assert (
        "Cannot apply lookup for base /SomethingUnknown to image with mode 1. "
        "Please share PDF with pypdf dev team"
    ) in caplog.text


def test_image_from_bytes__zero_data() -> None:
    mode = "RGB"
    size = (1, 1)
    data = b""

    with pytest.raises(EmptyImageDataError, match=r"Data is 0 bytes, cannot process an image from empty data\."):
        _image_from_bytes(mode, size, data)


def test_handle_flate__autodesk_indexed() -> None:
    reader = PdfReader(RESOURCE_ROOT / "AutoCad_Diagram.pdf")
    page = reader.pages[0]
    for name, image in page.images.items():
        assert isinstance(name, str)
        assert name.startswith("/")
        assert image.image is not None
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
            assert isinstance(name, str)
            assert name.startswith("/")


@pytest.mark.enable_socket
def test_get_mode_and_invert_color() -> None:
    url = "https://github.com/user-attachments/files/18381726/tika-957721.pdf"
    name = "tika-957721.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))
    page = reader.pages[12]
    for _name, image in page.images.items():  # noqa: PERF102
        assert image.image is not None
        image.image.load()


@pytest.mark.enable_socket
def test_get_imagemode__empty_array() -> None:
    url = "https://github.com/user-attachments/files/23050451/poc.pdf"
    name = "issue3499.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))
    page = reader.pages[0]

    with pytest.raises(expected_exception=PdfReadError, match=r"^ColorSpace field not found in .+"):
        image = page.images[0].image
        assert image is not None
        image.load()


def test_p_image_with_alpha_mask() -> None:
    # Generate the base image. Use TIFF as this is easy to do on the fly.
    image = Image.new(mode="P", size=(10, 10), color=0)
    image_data = BytesIO()
    image.save(image_data, format="tiff")

    # Set the common values.
    x_object = StreamObject()
    mask_object = StreamObject()
    for obj in [x_object, mask_object]:
        obj[NameObject(ImageAttributes.WIDTH)] = NumberObject(image.width)
        obj[NameObject(ImageAttributes.HEIGHT)] = NumberObject(image.height)
        obj[NameObject(StreamAttributes.FILTER)] = NameObject(FilterTypes.CCITT_FAX_DECODE)

    # Set the basic image data.
    x_object.set_data(image_data.getvalue())
    x_object[NameObject(ImageAttributes.COLOR_SPACE)] = TextStringObject("palette")

    # Generate the mask image. Will be a diagonal white stripe.
    image = Image.new(mode="1", size=(image.width, image.height))
    for i in range(10):
        image.putpixel((i, i), 1)
    image_data = BytesIO()
    image.save(image_data, format="tiff")

    # Set the mask data.
    mask_object.set_data(image_data.getvalue())
    mask_object[NameObject(ImageAttributes.COLOR_SPACE)] = TextStringObject("1bit")

    # Add the mask to the image.
    x_object[NameObject("/SMask")] = mask_object

    # Generate the output image and make sure that the diagonal stripe is present.
    extension, data, image = _xobj_to_image(x_object)
    assert extension == ".png"
    assert data.startswith(b"\x89PNG")
    for i in range(10):
        for j in range(10):
            assert image.getpixel((i, j)) == (0, 0, 0, 255 * (i == j))


@pytest.mark.enable_socket
def test_handle_flate__icc_based__image_mode_1() -> None:
    url = "https://github.com/user-attachments/files/23756943/pypdf_bug_3534_iccbased.pdf"
    name = "issue3534.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))
    page = reader.pages[0]

    image = page.images[0].image
    assert image is not None
    image.load()
    assert image.size == (64, 64)
    assert image.mode == "1"

    for y in range(64):
        for x in range(64):
            # Determine which chess square this pixel belongs to
            square_x = x // 8
            square_y = y // 8
            is_black_square = (square_x + square_y) % 2 == 1
            assert image.getpixel((x, y)) == 255 * int(not is_black_square)


@pytest.mark.skipif(
    condition=Version(PIL.__version__) < Version("12.1.0"),
    reason="Unsuitable Pillow version."
)
def test_handle_jpx__explicit_decode() -> None:
    stream = StreamObject()
    stream[NameObject("/BitsPerComponent")] = NumberObject(8)
    stream[NameObject("/ColorSpace")] = NameObject("/DeviceCMYK")
    stream[NameObject("/Decode")] = ArrayObject([1, 0, 1, 0, 1, 0, 1, 0])
    stream[NameObject("/Filter")] = NameObject("/JPXDecode")
    stream[NameObject("/Height")] = NumberObject(16)
    stream[NameObject("/Width")] = NumberObject(16)

    image = Image.new(mode="CMYK", size=(16, 16))
    for i in range(16):
        image.putpixel((i, i), 255)
    image_data = BytesIO()
    image.save(image_data, format="JPEG2000")
    stream.set_data(image_data.getvalue())
    image.save(image_data, format="JPEG2000")

    result = _xobj_to_image(x_object=stream)[2]
    for y in range(16):
        for x in range(16):
            assert result.getpixel((x, y)) == (255 * (x != y), 255, 255, 255), (x, y)
            assert image.getpixel((x, y)) == (255 * (x == y), 0, 0, 0), (x, y)


def test_bits2byte__limit() -> None:
    with pytest.raises(
            expected_exception=LimitReachedError,
            match=r"^Requested buffer size 76500000 exceeds limit of 75000000\.$"
    ):
        bits2byte(data=b"TEST", size=(9000, 8500), bits=8)


def test_bits2byte__truncated_data(caplog: pytest.LogCaptureFixture) -> None:
    # 4x4 image at 2 bits per sample needs 4 bytes; provide only 1.
    result = bits2byte(data=b"\x00", size=(4, 4), bits=2)
    assert result == bytes(16)
    assert "Image data is not rectangular. Adding padding." in caplog.text


def test_handle_flate__truncated_2bit_image(caplog: pytest.LogCaptureFixture) -> None:
    # A 3x3 indexed image at 2 bits per sample needs 3 bytes; provide only 1.
    # Padding the missing bytes lets the image still be loaded instead of
    # raising IndexError out of bits2byte.
    lookup = DecodedStreamObject()
    lookup.set_data(bytes([0, 0, 0, 10, 10, 10, 20, 20, 20, 30, 30, 30]))
    result = _handle_flate(
        size=(3, 3),
        data=b"\xe4",
        mode="2bits",
        color_space=ArrayObject(
            [NameObject("/Indexed"), NameObject("/DeviceRGB"), NumberObject(3), lookup]
        ),
        colors=1,
        obj_as_text="dummy",
    )
    image = result[0]
    image.load()
    assert image.mode == "RGB"
    assert image.size == (3, 3)
    assert get_image_data(image) == (
        (30, 30, 30), (20, 20, 20), (10, 10, 10),
        (0, 0, 0), (0, 0, 0), (0, 0, 0),
        (0, 0, 0), (0, 0, 0), (0, 0, 0),
    )
    assert "Image data is not rectangular. Adding padding." in caplog.text


def test_get_imagemode__color_components_out_of_range() -> None:
    """A component count above the known modes must not raise IndexError."""
    # The color space is not one of the recognized names, so the mode is
    # otherwise picked by indexing the mode table with the component count.
    # A crafted value larger than that table previously raised IndexError;
    # it should now fall back to the previous mode.
    assert _get_image_mode("/Unknown", 99, "L") == ("L", False)
    assert _get_image_mode("/Unknown", 99, "") == ("", False)


def test_xobj_to_image__color_components_out_of_range() -> None:
    """An image with an out-of-range /Colors value degrades to PdfReadError."""
    x_object = StreamObject()
    x_object[NameObject(ImageAttributes.WIDTH)] = NumberObject(4)
    x_object[NameObject(ImageAttributes.HEIGHT)] = NumberObject(4)
    x_object[NameObject("/BitsPerComponent")] = NumberObject(8)
    x_object[NameObject(ImageAttributes.COLOR_SPACE)] = NameObject("/Unknown")
    x_object[NameObject("/Colors")] = NumberObject(8)
    x_object.set_data(b"\x00" * 16)

    with pytest.raises(PdfReadError, match=r"^ColorSpace field not found in .+"):
        _xobj_to_image(x_object)


@pytest.mark.parametrize(
    "decode",
    [
        ArrayObject([NumberObject(1), NumberObject(0), NumberObject(1)]),
        ArrayObject([NumberObject(1)]),
        NumberObject(1),
    ],
    ids=["odd-length-array", "single-value-array", "not-an-array"],
)
def test_xobj_to_image__malformed_decode(
    decode: PdfObject, caplog: pytest.LogCaptureFixture
) -> None:
    """A /Decode without an even number of values must not raise IndexError."""
    x_object = StreamObject()
    x_object[NameObject(ImageAttributes.WIDTH)] = NumberObject(2)
    x_object[NameObject(ImageAttributes.HEIGHT)] = NumberObject(2)
    x_object[NameObject(ImageAttributes.BITS_PER_COMPONENT)] = NumberObject(8)
    x_object[NameObject(ImageAttributes.COLOR_SPACE)] = NameObject(ColorSpaces.DEVICE_GRAY)
    x_object[NameObject(StreamAttributes.FILTER)] = NameObject(FilterTypes.FLATE_DECODE)
    x_object[NameObject(ImageAttributes.DECODE)] = decode
    x_object.set_data(zlib.compress(bytes([0, 64, 128, 255])))

    _, _, image = _xobj_to_image(x_object)
    image.load()
    assert image.size == (2, 2)
    assert "Ignoring malformed /Decode array" in caplog.text


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("1", "8000000000"),
        ("RGB", "24000000000"),
        ("CMYK", "32000000000"),
    ],
)
def test_image_from_bytes__limit(mode: str, expected: str) -> None:
    with pytest.raises(
            expected_exception=LimitReachedError,
            match=rf"^Requested image buffer size {expected} exceeds limit 75000000\.$"
    ):
        _ = _image_from_bytes(mode=mode, size=(100_000, 80_000), data=b"")
