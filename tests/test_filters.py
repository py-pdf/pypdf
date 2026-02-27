"""Test the pypdf.filters module."""
import os
import string
import subprocess
import sys
import zlib
from io import BytesIO
from itertools import product as cartesian_product
from pathlib import Path
from typing import cast
from unittest import mock

import pytest
from PIL import Image, ImageOps

from pypdf import PdfReader, PdfWriter
from pypdf.errors import DependencyError, DeprecationError, LimitReachedError, PdfReadError, PdfStreamError
from pypdf.filters import (
    ASCII85Decode,
    ASCIIHexDecode,
    CCITParameters,
    CCITTFaxDecode,
    CCITTParameters,
    FlateDecode,
    JBIG2Decode,
    RunLengthDecode,
    decode_stream_data,
    decompress,
)
from pypdf.generic import (
    ArrayObject,
    BooleanObject,
    ContentStream,
    DictionaryObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    StreamObject,
    TextStringObject,
)

from . import RESOURCE_ROOT, PILContext, get_data_from_url
from .test_encryption import HAS_AES
from .test_images import image_similarity
from .utils import get_image_data

filter_inputs = (
    string.ascii_letters,
    string.ascii_lowercase,
    string.ascii_uppercase,
    string.digits,
    string.hexdigits,
    string.octdigits,
    string.punctuation,
    string.printable,
    string.whitespace,  # Add more
)


@pytest.mark.parametrize(
    ("predictor", "s"), list(cartesian_product([1], filter_inputs))
)
def test_flate_decode_encode(predictor, s):
    """FlateDecode encode() and decode() methods work as expected."""
    codec = FlateDecode()
    s = s.encode()
    encoded = codec.encode(s)
    assert codec.decode(encoded, DictionaryObject({"/Predictor": predictor})) == s


def test_flatedecode_unsupported_predictor():
    """
    FlateDecode raises PdfReadError for unsupported predictors.

    Predictor values outside the ranges [1, 2] and [10, 15] are not supported.

    Checks that a PdfReadError is raised when decoding with unsupported predictors.
    """
    codec = FlateDecode()
    predictors = (-10, -1, 0, 3, 9, 16, 20, 100)

    for predictor, s in cartesian_product(predictors, filter_inputs):
        s = s.encode()
        with pytest.raises(PdfReadError):
            codec.decode(codec.encode(s), DictionaryObject({NameObject("/Predictor"): NumberObject(predictor)}))


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (">", b""),
        (
            "6162636465666768696a6b6c6d6e6f707172737475767778797a>",
            string.ascii_lowercase.encode(),
        ),
        (
            "4142434445464748494a4b4c4d4e4f505152535455565758595a>",
            string.ascii_uppercase.encode(),
        ),
        (
            "6162636465666768696a6b6c6d6e6f707172737475767778797a4142434445464748494a4b4c4d4e4f505152535455565758595a>",
            string.ascii_letters.encode(),
        ),
        ("30313233343536373839>", string.digits.encode()),
        (
            "3  031323334353637   3839>",
            string.digits.encode(),
        ),  # Same as previous, but whitespaced
        ("30313233343536373839616263646566414243444546>", string.hexdigits.encode()),
        ("20090a0d0b0c>", string.whitespace.encode()),
        # Odd number of hexadecimal digits behaves as if a 0 (zero) followed the last digit
        ("3938373635343332313>", string.digits[::-1].encode()),
    ],
    ids=[
        "empty",
        "ascii_lowercase",
        "ascii_uppercase",
        "ascii_letters",
        "digits",
        "digits_whitespace",
        "hexdigits",
        "whitespace",
        "odd_number",
    ],
)
def test_ascii_hex_decode_method(data, expected):
    """
    Feeds a bunch of values to ASCIIHexDecode.decode() and ensures the
    correct output is returned.
    """
    assert ASCIIHexDecode.decode(data) == expected


def test_ascii_hex_decode_missing_eod(caplog):
    """ASCIIHexDecode.decode() logs warning when no EOD character is present."""
    ASCIIHexDecode.decode("")
    assert "missing EOD in ASCIIHexDecode, check if output is OK" in caplog.text


@pytest.mark.enable_socket
def test_decode_ahx():
    """
    See #1979
    Gray Image in CMYK : requiring reverse
    """
    reader = PdfReader(BytesIO(get_data_from_url(name="NewJersey.pdf")))
    for p in reader.pages:
        _ = list(p.images.keys())


def test_ascii85decode_with_overflow():
    inputs = (
        v + "~>"
        for v in "\x01\x02\x03\x04\x05\x06\x07\x08\x0e\x0f"
        "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a"
        "\x1b\x1c\x1d\x1e\x1fvwxy{|}~\x7f\x80\x81\x82"
        "\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d"
        "\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98"
        "\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0¡¢£¤¥¦§¨©ª«¬"
        "\xad®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇ"
    )

    for i in inputs:
        with pytest.raises(ValueError):
            ASCII85Decode.decode(i)


def test_ascii85decode_five_zero_bytes():
    """
    ASCII85Decode handles the special case of five zero bytes correctly.

    ISO 32000-1:2008 §7.4.3:

    «As a special case, if all five bytes are 0, they shall be represented by
    the character with code 122 (z) instead of by five exclamation points
    (!!!!!).»
    """
    inputs = ("z", "zz", "zzz")
    exp_outputs = (
        b"\x00\x00\x00\x00",
        b"\x00\x00\x00\x00" * 2,
        b"\x00\x00\x00\x00" * 3,
    )

    assert ASCII85Decode.decode("!!!!!~>") == ASCII85Decode.decode("z~>")

    for expected, i in zip(exp_outputs, inputs):
        assert ASCII85Decode.decode(i + "~>") == expected


def test_ccitparameters():
    with pytest.raises(
        DeprecationError,
        match=r"CCITParameters is deprecated and was removed in pypdf 6\.0\.0\. Use CCITTParameters instead",
    ):
        CCITParameters()


def test_ccittparameters():
    params = CCITTParameters()
    assert params.K == 0  # zero is the default according to page 78
    assert params.BlackIs1 is False
    assert params.group == 3


@pytest.mark.parametrize(
    ("parameters", "expected_k", "expected_black_is_1"),
    [
        (None, 0, False),
        (
            ArrayObject([{"/K": NumberObject(1)}, {"/Columns": NumberObject(13)}, {"/BlackIs1": BooleanObject(True)}]),
            1, True
        ),
    ],
)
def test_ccitt_get_parameters(parameters, expected_k, expected_black_is_1):
    parameters = CCITTFaxDecode._get_parameters(parameters=parameters, rows=0)
    assert parameters.K == expected_k  # noqa: SIM300
    assert parameters.BlackIs1 == expected_black_is_1


def test_ccitt_get_parameters__indirect_object():
    class Pdf:
        def get_object(self, reference) -> NumberObject:
            return NumberObject(42)

    parameters = CCITTFaxDecode._get_parameters(
        parameters=None, rows=IndirectObject(13, 1, Pdf())
    )
    assert parameters.rows == 42


def test_ccitt_fax_decode():
    data = b""
    parameters = DictionaryObject(
        {"/K": NumberObject(-1), "/Columns": NumberObject(17)}
    )

    # This is the header of an empty TIFF image.
    assert CCITTFaxDecode.decode(data, parameters) == (
        b"II*\x00\x08\x00\x00\x00\x08\x00\x00\x01\x04\x00\x01\x00\x00\x00\x11\x00"
        b"\x00\x00\x01\x01\x04\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x01"
        b"\x03\x00\x01\x00\x00\x00\x01\x00\x00\x00\x03\x01\x03\x00\x01\x00"
        b"\x00\x00\x04\x00\x00\x00\x06\x01\x03\x00\x01\x00\x00\x00\x00\x00"
        b"\x00\x00\x11\x01\x04\x00\x01\x00\x00\x00l\x00\x00\x00\x16\x01"
        b"\x04\x00\x01\x00\x00\x00\x00\x00\x00\x00\x17\x01\x04\x00\x01\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
    )


@pytest.mark.enable_socket
def test_decompress_zlib_error(caplog):
    reader = PdfReader(BytesIO(get_data_from_url(name="tika-952445.pdf")))
    for page in reader.pages:
        page.extract_text()
    assert "incorrect startxref pointer(3)" in caplog.text


@pytest.mark.enable_socket
def test_lzw_decode_neg1():
    reader = PdfReader(BytesIO(get_data_from_url(name="tika-921632.pdf")))
    page = reader.pages[47]
    assert page.extract_text().startswith("Chapter 2")


@pytest.mark.enable_socket
def test_issue_399():
    reader = PdfReader(BytesIO(get_data_from_url(name="tika-976970.pdf")))
    reader.pages[1].extract_text()


@pytest.mark.enable_socket
def test_image_without_pillow(tmp_path):
    env = os.environ.copy()
    env["COVERAGE_PROCESS_START"] = "pyproject.toml"

    name = "tika-914102.pdf"
    pdf_path = Path(__file__).parent / "pdf_cache" / name
    pdf_path_str = pdf_path.resolve().as_posix()

    source_file = tmp_path / "script.py"
    source_file.write_text(
        f"""
import sys
from pypdf import PdfReader

import pytest


sys.modules["PIL"] = None
reader = PdfReader("{pdf_path_str}", strict=True)

for page in reader.pages:
    with pytest.raises(ImportError) as exc:
        page.images[0]
    assert exc.value.args[0] == (
        "pillow is required to do image extraction. "
        "It can be installed via 'pip install pypdf[image]'"
    ), exc.value.args[0]
"""
    )

    try:
        env["PYTHONPATH"] = "." + os.pathsep + env["PYTHONPATH"]
    except KeyError:
        env["PYTHONPATH"] = "."
    result = subprocess.run(  # noqa: S603  # We have the control here.
        [sys.executable, source_file],
        capture_output=True,
        env=env,
    )
    assert result.returncode == 0
    assert result.stdout == b""
    assert (
        result.stderr.replace(b"\r", b"")
        == b"Superfluous whitespace found in object header b'4' b'0'\n"
    )


@pytest.mark.enable_socket
def test_issue_1737():
    reader = PdfReader(BytesIO(get_data_from_url(name="iss1737.pdf")))
    reader.pages[0]["/Resources"]["/XObject"]["/Im0"].get_data()
    reader.pages[0]["/Resources"]["/XObject"]["/Im1"].get_data()
    reader.pages[0]["/Resources"]["/XObject"]["/Im2"].get_data()


@pytest.mark.enable_socket
def test_pa_image_extraction():
    """
    PNG images with PA mode can be extracted.

    This is a regression test for issue #1801
    """
    reader = PdfReader(BytesIO(get_data_from_url(name="issue-1801.pdf")))

    page0 = reader.pages[0]
    images = page0.images
    assert len(images) == 1
    assert images[0].name == "Im1.png"

    # Ensure visual appearance
    expected_data = BytesIO(get_data_from_url(name="issue-1801.png"))
    assert image_similarity(expected_data, images[0].image) == 1


@pytest.mark.enable_socket
def test_1bit_image_extraction():
    """Cf issue #1814"""
    reader = PdfReader(BytesIO(get_data_from_url(name="grimm10")))
    for p in reader.pages:
        p.images


@pytest.mark.enable_socket
def test_png_transparency_reverse():
    """Cf issue #1599"""
    pdf_path = RESOURCE_ROOT / "labeled-edges-center-image.pdf"
    reader = PdfReader(pdf_path)
    refimg = Image.open(
        BytesIO(get_data_from_url(name="labeled-edges-center-image.png"))
    )
    data = reader.pages[0].images[0]
    img = Image.open(BytesIO(data.data))
    assert ".jp2" in data.name
    assert get_image_data(img) == get_image_data(refimg)


@pytest.mark.enable_socket
def test_iss1787():
    """Cf issue #1787"""
    reader = PdfReader(BytesIO(get_data_from_url(name="pdf_font_garbled.pdf")))
    refimg = Image.open(BytesIO(get_data_from_url(name="watermark1.png")))
    data = reader.pages[0].images[0]
    img = Image.open(BytesIO(data.data))
    assert ".png" in data.name
    assert get_image_data(img) == get_image_data(refimg)
    obj = data.indirect_reference.get_object()
    obj["/DecodeParms"][NameObject("/Columns")] = NumberObject(1000)
    obj.decoded_self = None
    with pytest.raises(expected_exception=PdfReadError, match=r"^Unsupported PNG filter 244$"):
        _ = reader.pages[0].images[0]


@pytest.mark.enable_socket
def test_tiff_predictor():
    """Decode Tiff Predictor 2 Images"""
    reader = PdfReader(BytesIO(get_data_from_url(name="tika-977609.pdf")))
    refimg = Image.open(BytesIO(get_data_from_url(name="tifimage.png")))
    data = reader.pages[0].images[0]
    img = Image.open(BytesIO(data.data))
    assert ".png" in data.name
    assert get_image_data(img) == get_image_data(refimg)


@pytest.mark.enable_socket
def test_rgba():
    """Decode RGB with transparency"""
    with PILContext():
        reader = PdfReader(BytesIO(get_data_from_url(name="tika-972174.pdf")))
        data = reader.pages[0].images[0]
        assert ".jp2" in data.name
        similarity = image_similarity(
            data.image, BytesIO(get_data_from_url(name="tika-972174_p0-im0.png"))
        )
        assert similarity > 0.99


@pytest.mark.enable_socket
@pytest.mark.skipif(not HAS_AES, reason="No AES implementation")
def test_cmyk():
    """Decode CMYK"""
    # JPEG compression
    reader = PdfReader(BytesIO(get_data_from_url(name="Vitocal.pdf")))
    refimg = BytesIO(get_data_from_url(name="VitocalImage.png"))
    data = reader.pages[1].images[0]
    assert data.image.mode == "CMYK"
    assert ".jpg" in data.name
    assert image_similarity(data.image, refimg) > 0.99
    # deflate
    reader = PdfReader(BytesIO(get_data_from_url(name="cmyk_deflate.pdf")))
    refimg = BytesIO(get_data_from_url(name="cmyk_deflate.tif"))
    data = reader.pages[0].images[0]
    assert data.image.mode == "CMYK"
    assert ".tif" in data.name
    assert image_similarity(data.image, refimg) > 0.999  # lossless compression expected


@pytest.mark.enable_socket
def test_iss1863():
    """Test doc from iss1863"""
    reader = PdfReader(BytesIO(get_data_from_url(name="o1whh9b3.pdf")))
    for p in reader.pages:
        for i in p.images:
            i.name


@pytest.mark.enable_socket
def test_read_images():
    reader = PdfReader(BytesIO(get_data_from_url(name="selbst.72916.pdf")))
    page = reader.pages[0]
    for _ in page.images:
        pass


@pytest.mark.enable_socket
def test_cascaded_filters_images():
    reader = PdfReader(BytesIO(get_data_from_url(name="iss1912.pdf")))
    # for focus, analyse the page 23
    for p in reader.pages:
        for i in p.images:
            _ = i.name, i.image


@pytest.mark.enable_socket
def test_calrgb():
    reader = PdfReader(BytesIO(get_data_from_url(name="calRGB.pdf")))
    reader.pages[0].images[0]


@pytest.mark.enable_socket
def test_index_lookup():
    """The lookup is provided as an str and bytes"""
    reader = PdfReader(BytesIO(get_data_from_url(name="2023USDC.pdf")))
    # TextStringObject Lookup
    refimg = BytesIO(get_data_from_url(name="iss1982_im1.png"))
    data = reader.pages[0].images[-1]
    assert data.image.mode == "RGB"
    assert image_similarity(data.image, refimg) > 0.999
    # ByteStringObject Lookup
    refimg = BytesIO(get_data_from_url(name="iss1982_im2.png"))
    data = reader.pages[-1].images[-1]
    assert data.image.mode == "RGB"
    assert image_similarity(data.image, refimg) > 0.999
    # indexed CMYK images
    # currently with a TODO as we convert the palette to RGB
    reader = PdfReader(BytesIO(get_data_from_url(name="tika-972174.pdf")))
    refimg = Image.open(BytesIO(get_data_from_url(name="usa.png")))
    data = reader.pages[0].images["/Im3"]
    # assert data.image.mode == "PA" but currently "RGBA"
    assert image_similarity(data.image, refimg) > 0.999


@pytest.mark.enable_socket
def test_2bits_image():
    """From #1954, test with 2bits image. TODO: 4bits also"""
    reader = PdfReader(BytesIO(get_data_from_url(name="paid.pdf")))
    url_png = "https://user-images.githubusercontent.com/4083478/253568117-ca95cc85-9dea-4145-a5e0-032f1c1aa322.png"
    name_png = "Paid.png"
    refimg = BytesIO(get_data_from_url(url_png, name=name_png))
    data = reader.pages[0].images[0]
    assert image_similarity(data.image, refimg) > 0.99


@pytest.mark.enable_socket
def test_gray_devicen_cmyk():
    """
    Cf #1979
    Gray Image in CMYK : requiring reverse
    """
    url = "https://github.com/py-pdf/pypdf/files/12080338/example_121.pdf"
    name = "gray_cmyk.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    url_png = "https://user-images.githubusercontent.com/4083478/254545494-42df4949-1557-4f2d-acca-6be6e8de1122.png"
    name_png = "velo.png"
    refimg = BytesIO(get_data_from_url(url_png, name=name_png))
    data = reader.pages[0].images[0]
    assert data.image.mode == "L"
    assert image_similarity(data.image, refimg) > 0.999


@pytest.mark.enable_socket
def test_runlengthdecode():
    """From #1954, test with 2bits image. TODO: 4bits also"""
    url = "https://github.com/py-pdf/pypdf/files/12159941/out.pdf"
    name = "RunLengthDecode.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    url_png = "https://user-images.githubusercontent.com/4083478/255940800-6d63972e-a3d6-4cf9-aa6f-0793af24cded.png"
    name_png = "RunLengthDecode.png"
    refimg = BytesIO(get_data_from_url(url_png, name=name_png))
    data = reader.pages[0].images[0]
    assert image_similarity(data.image, refimg) > 0.999
    url = "https://github.com/py-pdf/pypdf/files/12162905/out.pdf"
    name = "FailedRLE1.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    reader.pages[0].images[0]
    url = "https://github.com/py-pdf/pypdf/files/12162926/out.pdf"
    name = "FailedRLE2.pdf"
    reader.pages[0].images[0]


@pytest.mark.enable_socket
def test_gray_separation_cmyk():
    """
    Cf #1955
    Gray Image in Separation/RGB : requiring reverse
    """
    url = "https://github.com/py-pdf/pypdf/files/12143372/tt.pdf"
    name = "TestWithSeparationBlack.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    url_png = "https://user-images.githubusercontent.com/4083478/254545494-42df4949-1557-4f2d-acca-6be6e8de1122.png"
    name_png = "velo.png"  # reused
    refimg = BytesIO(get_data_from_url(url_png, name=name_png))
    data = reader.pages[0].images[0]
    assert data.image.mode == "L"
    assert image_similarity(data.image, refimg) > 0.999


@pytest.mark.enable_socket
def test_singleton_device():
    """From #2023"""
    url = "https://github.com/py-pdf/pypdf/files/12177287/tt.pdf"
    name = "pypdf_with_arr_deviceRGB.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    reader.pages[0].images[0]


@pytest.mark.enable_socket
def test_jpx_no_spacecode():
    """From #2061"""
    url = "https://github.com/py-pdf/pypdf/files/12253581/tt2.pdf"
    name = "jpx_no_spacecode.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    im = reader.pages[0].images[0]
    # create an object without filter and without colorspace
    # just for coverage
    del im.indirect_reference.get_object()["/Filter"]
    with pytest.raises(PdfReadError) as exc:
        reader.pages[0].images[0]
    assert exc.value.args[0].startswith("ColorSpace field not found")


@pytest.mark.enable_socket
def test_encodedstream_lookup():
    """From #2124"""
    url = "https://github.com/py-pdf/pypdf/files/12455580/10.pdf"
    name = "iss2124.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    reader.pages[12].images[0]


@pytest.mark.enable_socket
def test_convert_1_to_la():
    """From #2165"""
    url = "https://github.com/py-pdf/pypdf/files/12543290/whitepaper.WBT.token.blockchain.whitepaper.pdf"
    name = "iss2165.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    for i in reader.pages[13].images:
        _ = i


@pytest.mark.enable_socket
def test_nested_device_n_color_space():
    """From #2240"""
    url = "https://github.com/py-pdf/pypdf/files/12814018/out1.pdf"
    name = "issue2240.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    reader.pages[0].images[0]


@pytest.mark.enable_socket
@pytest.mark.skipif(not HAS_AES, reason="No AES implementation")
def test_flate_decode_with_image_mode_1():
    """From #2248"""
    url = "https://github.com/py-pdf/pypdf/files/12847339/Prototype-Declaration-VDE4110-HYD-5000-20000-ZSS-DE.pdf"
    name = "issue2248.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    for image in reader.pages[7].images:
        _ = image


@pytest.mark.enable_socket
def test_flate_decode_with_image_mode_1__whitespace_at_end_of_lookup():
    """From #2331"""
    url = "https://github.com/py-pdf/pypdf/files/13611048/out1.pdf"
    name = "issue2331.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    reader.pages[0].images[0]


@pytest.mark.enable_socket
def test_ascii85decode__invalid_end__recoverable(caplog):
    """From #2996"""
    url = "https://github.com/user-attachments/files/18050808/1af7d56a-5c8c-4914-85b3-b2536a5525cd.pdf"
    name = "issue2996.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))

    page = reader.pages[1]
    assert page.extract_text() == ""
    assert "Ignoring missing Ascii85 end marker." in caplog.text


def test_ascii85decode__non_recoverable(caplog):
    # Without our custom handling, this would complain about the final `~>` being missing.
    data = "äöüß"
    with pytest.raises(ValueError, match="Non-Ascii85 digit found: Ã"):
        ASCII85Decode.decode(data)
    assert "Ignoring missing Ascii85 end marker." in caplog.text
    caplog.clear()

    data += "~>"
    with pytest.raises(ValueError, match="Non-Ascii85 digit found: Ã"):
        ASCII85Decode.decode(data)
    assert caplog.text == ""


def test_ascii85decode__ignore_whitespaces(caplog):
    """Whitespace characters must be silently ignored"""
    data = b"Cqa;:3k~\n>"
    result = ASCII85Decode.decode(data)
    assert result == b"l\xbe`\x8d:"


@pytest.mark.enable_socket
def test_ccitt_fax_decode__black_is_1():
    url = "https://github.com/user-attachments/files/19288881/imagemagick-CCITTFaxDecode_BlackIs1-true.pdf"
    name = "issue3193.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    other_reader = PdfReader(RESOURCE_ROOT / "imagemagick-CCITTFaxDecode.pdf")

    actual_image = reader.pages[0].images[0].image
    expected_image_inverted = other_reader.pages[0].images[0].image
    expected_pixels = get_image_data(ImageOps.invert(expected_image_inverted))
    actual_pixels = get_image_data(actual_image)
    assert expected_pixels == actual_pixels

    # AttributeError: 'NullObject' object has no attribute 'get'
    data_modified = get_data_from_url(url, name=name).replace(
        b"/DecodeParms [ << /K -1 /BlackIs1 true /Columns 16 /Rows 16 >> ]",
        b"/DecodeParms [ null ]"
    )
    reader = PdfReader(BytesIO(data_modified))
    _ = reader.pages[0].images[0].image


@pytest.mark.enable_socket
def test_flate_decode__image_is_none_due_to_size_limit(caplog):
    url = "https://github.com/user-attachments/files/19464256/file.pdf"
    name = "issue3220.pdf"

    with mock.patch("pypdf.filters.ZLIB_MAX_OUTPUT_LENGTH", 0):
        reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
        images = reader.pages[0].images
        assert len(images) == 1
        image = images[0]
        assert image.name == "Im0.png"
        assert image.image is None

    assert (
        "Failed loading image: Image size (180000000 pixels) exceeds limit of "
        "178956970 pixels, could be decompression bomb DOS attack."
    ) in caplog.messages


@pytest.mark.enable_socket
def test_flate_decode__not_rectangular(caplog):
    url = "https://github.com/user-attachments/files/19663603/issue3241_compressed.txt"
    name = "issue3241.txt"
    data = get_data_from_url(url, name=name)
    decode_parms = DictionaryObject()
    decode_parms[NameObject("/Predictor")] = NumberObject(15)
    decode_parms[NameObject("/Columns")] = NumberObject(4881)
    actual = FlateDecode.decode(data=data, decode_parms=decode_parms)
    actual_image = Image.frombytes(mode="1", size=(4881, 81), data=actual)

    url = "https://github.com/user-attachments/assets/c5695850-c076-4255-ab72-7c86851a4a04"
    name = "issue3241.png"
    expected_data = BytesIO(get_data_from_url(url, name=name))
    assert image_similarity(expected_data, actual_image) == 1
    assert caplog.messages == ["Image data is not rectangular. Adding padding."]


def test_jbig2decode__binary_errors():
    with mock.patch("pypdf.filters.JBIG2DEC_BINARY", None), \
            pytest.raises(DependencyError, match=r"jbig2dec binary is not available\."):
        JBIG2Decode.decode(b"dummy")

    result = subprocess.CompletedProcess(
        args=["dummy"], returncode=0, stdout=b"",
        stderr=(
            b"jbig2dec: unrecognized option '--embedded'\n"
            b"Usage: jbig2dec [options] <file.jbig2>\n"
            b"   or  jbig2dec [options] <global_stream> <page_stream>\n"
        )
    )
    with mock.patch("pypdf.filters.subprocess.run", return_value=result), \
            mock.patch("pypdf.filters.JBIG2DEC_BINARY", "/usr/bin/jbig2dec"), \
            pytest.raises(DependencyError, match=r"jbig2dec>=0.19 is required\."):
        JBIG2Decode.decode(b"dummy")

    result = subprocess.CompletedProcess(
        args=["dummy"], returncode=0, stdout=b"",
        stderr=(
            b"jbig2dec: unrecognized option '-M'\n"
            b"Usage: jbig2dec [options] <file.jbig2>\n"
            b"   or  jbig2dec [options] <global_stream> <page_stream>\n"
        )
    )
    with mock.patch("pypdf.filters.subprocess.run", return_value=result), \
            mock.patch("pypdf.filters.JBIG2DEC_BINARY", "/usr/bin/jbig2dec"), \
            pytest.raises(DependencyError, match=r"jbig2dec>=0.19 is required\."):
        JBIG2Decode.decode(b"dummy")


@pytest.mark.skipif(condition=not JBIG2Decode._is_binary_compatible(), reason="Requires recent jbig2dec")
def test_jbig2decode__edge_cases(caplog):
    image_data = (
        b'\x00\x00\x00\x010\x00\x01\x00\x00\x00\x13\x00\x00\x00\x05\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x06"'
        b'\x00\x01\x00\x00\x00\x1c\x00\x00\x00\x05\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x9f\xa8_\xff\xac'

    )
    jbig2_globals = b"\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x18\x00\x00\x03\xff\xfd\xff\x02\xfe\xfe\xfe\x00\x00\x00\x01\x00\x00\x00\x01R\xd0u7\xff\xac"  # noqa: E501

    # Validation: Is our image data valid?
    content_stream = ContentStream(stream=None, pdf=None)
    content_stream.set_data(jbig2_globals)
    result = JBIG2Decode.decode(image_data, decode_parms=DictionaryObject({"/JBIG2Globals": content_stream}))
    image = Image.open(BytesIO(result), formats=("PNG", "PPM"))
    for x in range(5):
        for y in range(5):
            assert image.getpixel((x, y)) == (255 if x < 3 else 0), (x, y)
    assert caplog.messages == []

    # No decode_params. Completely white image.
    result = JBIG2Decode.decode(image_data)
    image = Image.open(BytesIO(result), formats=("PNG", "PPM"))
    for x in range(5):
        for y in range(5):
            assert image.getpixel((x, y)) == 255, (x, y)
    assert caplog.messages == [
        "jbig2dec WARNING text region refers to no symbol dictionaries (segment 0x00000002)",
        "jbig2dec WARNING ignoring out of range symbol ID (0/0) (segment 0x00000002)"
    ]
    caplog.clear()

    # JBIG2Globals is NULL. Completely white image.
    result = JBIG2Decode.decode(image_data, decode_parms=DictionaryObject({"/JBIG2Globals": NullObject()}))
    image = Image.open(BytesIO(result), formats=("PNG", "PPM"))
    for x in range(5):
        for y in range(5):
            assert image.getpixel((x, y)) == 255, (x, y)
    assert caplog.messages == [
        "jbig2dec WARNING text region refers to no symbol dictionaries (segment 0x00000002)",
        "jbig2dec WARNING ignoring out of range symbol ID (0/0) (segment 0x00000002)"
    ]
    caplog.clear()

    # JBIG2Globals is DictionaryObject. Completely white image.
    result = JBIG2Decode.decode(image_data, decode_parms=DictionaryObject({"/JBIG2Globals": DictionaryObject()}))
    image = Image.open(BytesIO(result), formats=("PNG", "PPM"))
    for x in range(5):
        for y in range(5):
            assert image.getpixel((x, y)) == 255, (x, y)
    assert caplog.messages == [
        "jbig2dec WARNING text region refers to no symbol dictionaries (segment 0x00000002)",
        "jbig2dec WARNING ignoring out of range symbol ID (0/0) (segment 0x00000002)"
    ]
    caplog.clear()

    # Invalid input.
    with pytest.raises(PdfStreamError, match=r"Unable to decode JBIG2 data\. Exit code: 1"):
        JBIG2Decode.decode(b"aaaaaa")
    assert caplog.messages == [
        "jbig2dec FATAL ERROR page has no image, cannot be completed",
        "jbig2dec WARNING unable to complete page"
    ]


@pytest.mark.timeout(timeout=30, method="thread")
@pytest.mark.enable_socket
def test_flate_decode_stream_with_faulty_tail_bytes():
    """
    Test for #3332

    The test ensures two things:
        1. stream can be decoded at all
        2. decoding doesn't falls through to last fallback in try-except blocks
           that is too slow and takes ages for this stream
    """
    data = get_data_from_url(
        url="https://github.com/user-attachments/files/20901522/faulty_stream_tail_example.1.pdf",
        name="faulty_stream_tail_example.1.pdf"
    )
    expected = get_data_from_url(
        url="https://github.com/user-attachments/files/20941717/decoded.dat.txt",
        name="faulty_stream_tail_example.1.decoded.dat"
    )
    reader = PdfReader(BytesIO(data))
    obj = reader.get_object(IndirectObject(182, 0, reader))
    assert cast(StreamObject, obj).get_data() == expected


@pytest.mark.enable_socket
def test_rle_decode_with_faulty_tail_byte_in_multi_encoded_stream(caplog):
    """
    Test for #3355

    The test ensures that the inner RLE encoded stream can be decoded,
    because this stream contains an extra faulty newline byte in the
    end that can be ignored during decoding.
    """
    data = get_data_from_url(
        url="https://github.com/user-attachments/files/21038398/test_data_rle.txt",
        name="multi_decoding_example_with_faulty_tail_byte.pdf"
    )
    reader = PdfReader(BytesIO(data))
    obj = reader.get_object(IndirectObject(60, 0, reader))
    cast(StreamObject, obj).get_data()
    assert "Found trailing newline in stream data, check if output is OK" in caplog.messages


@pytest.mark.enable_socket
def test_rle_decode_exception_with_corrupted_stream(caplog):
    """
    Additional Test to #3355

    This test must report the EOD warning during RLE decoding and ensures
    that we do not fail during code coverage analyses in the git PR pipeline.
    """
    data = get_data_from_url(
        url="https://github.com/user-attachments/files/21052626/rle_stream_with_error.txt",
        name="rle_stream_with_error.txt"
    )
    decoded = RunLengthDecode.decode(data)
    assert decoded.startswith(b"\x01\x01\x01\x01\x01\x01\x01\x02\x02\x02\x02\x02\x02\x02\x03\x03")
    assert decoded.endswith(b"\x87\x83\x83\x83\x83\x83\x83\x83]]]]]]]RRRRRRRX\xa5")
    assert len(decoded) == 1048576
    assert caplog.messages == ["Early EOD in RunLengthDecode, check if output is OK"]


def test_decompress():
    data = string.printable.encode("utf-8") + string.printable[::-1].encode("utf-8")
    compressed = FlateDecode.encode(data)

    # Decompress regularly.
    decompressed = decompress(compressed)
    assert decompressed == data

    # Decompress byte-wise.
    with mock.patch("pypdf.filters._decompress_with_limit", side_effect=zlib.error):
        decompressed = decompress(compressed)
        assert decompressed == data

    # Decompress byte-wise with very low output limit.
    with mock.patch("pypdf.filters._decompress_with_limit", side_effect=zlib.error), \
            mock.patch("pypdf.filters.ZLIB_MAX_OUTPUT_LENGTH", len(compressed) - 13), \
            pytest.raises(
                LimitReachedError, match=r"^Limit reached while decompressing\. 12 bytes remaining\.$"
            ):
        decompress(compressed)

    # Decompress byte-wise with input limit.
    with mock.patch("pypdf.filters.ZLIB_MAX_RECOVERY_INPUT_LENGTH", 1000), \
            pytest.raises(
                LimitReachedError, match=r"^Recovery limit reached while decompressing\. 336 bytes remaining\.$"
            ):
        decompress(b"A" * 1337)


def test_decompress__logging_on_invalid_data(caplog):
    """We do not like suddenly getting empty outputs for non-empty inputs without a warning."""
    codec = FlateDecode()
    encoded = codec.encode(b"My test string")
    assert len(encoded) > 5
    assert codec.decode(encoded[5:]) == b""
    assert caplog.messages == ["Error -3 while decompressing data: incorrect header check"]


def test_ccittfaxdecode__ccf_inline():
    writer = PdfWriter(clone_from=RESOURCE_ROOT / "jpeg.pdf")
    page = writer.pages[0]
    writer.remove_images()

    image_data = (
        b"\nBI\n  /W 16\n  /H 16\n  /CS /G\n  /BPC 1\n  /F [/CCF]\n"
        b"  /DP [ << /K -1 /BlackIs1 false /Columns 16 /Rows 16 >> ]\nID\n"
        b"&\xa0\xbf\xcc9\x14|G#\x1f\xff\xf1\xcc9\x18\xfe\xbbX\xfc\x00@\x04"
        b"\nEI\n"
    )
    content_stream = page.get_contents()
    content_stream.set_data(
        content_stream.get_data().replace(b"/Im4 Do", b"").replace(b"\nET", image_data)
    )
    page.replace_contents(content_stream)

    expected = PdfReader(RESOURCE_ROOT / "imagemagick-CCITTFaxDecode.pdf").pages[0].images[0].image
    assert get_image_data(expected) == get_image_data(page.images[0].image)


def test_dctdecode__dct_inline():
    writer = PdfWriter(clone_from=RESOURCE_ROOT / "jpeg.pdf")
    page = writer.pages[0]
    writer.remove_images()

    image_data = (
        b"\nBI\n  /W 16\n  /H 16\n  /CS /G\n  /BPC 8\n  /F [/DCT]\nID\n"
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x01,\x01,\x00\x00\xff\xfe\x00\x13Created with GIMP\xff\xe2"
        b"\x02\xb0ICC_PROFILE\x00\x01\x01\x00\x00\x02\xa0lcms\x040\x00\x00mntrRGB XYZ \x07\xe6\x00\x04\x00\x0f\x00"
        b"\t\x00\x1d\x007acspAPPL\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\xf6\xd6\x00\x01\x00\x00\x00\x00\xd3-lcms\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\rdesc\x00\x00\x01 \x00\x00\x00@cprt\x00\x00\x01`"
        b"\x00\x00\x006wtpt\x00\x00\x01\x98\x00\x00\x00\x14chad\x00\x00\x01\xac\x00\x00\x00,rXYZ\x00\x00\x01\xd8"
        b"\x00\x00\x00\x14bXYZ\x00\x00\x01\xec\x00\x00\x00\x14gXYZ\x00\x00\x02\x00\x00\x00\x00\x14rTRC\x00\x00"
        b"\x02\x14\x00\x00\x00 gTRC\x00\x00\x02\x14\x00\x00\x00 bTRC\x00\x00\x02\x14\x00\x00\x00 chrm\x00\x00"
        b"\x024\x00\x00\x00$dmnd\x00\x00\x02X\x00\x00\x00$dmdd\x00\x00\x02|\x00\x00\x00$mluc\x00\x00\x00\x00"
        b"\x00\x00\x00\x01\x00\x00\x00\x0cenUS\x00\x00\x00$\x00\x00\x00\x1c\x00G\x00I\x00M\x00P\x00 \x00b\x00"
        b"u\x00i\x00l\x00t\x00-\x00i\x00n\x00 \x00s\x00R\x00G\x00Bmluc\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00"
        b"\x00\x0cenUS\x00\x00\x00\x1a\x00\x00\x00\x1c\x00P\x00u\x00b\x00l\x00i\x00c\x00 \x00D\x00o\x00m\x00a"
        b"\x00i\x00n\x00\x00XYZ \x00\x00\x00\x00\x00\x00\xf6\xd6\x00\x01\x00\x00\x00\x00\xd3-sf32\x00\x00\x00"
        b"\x00\x00\x01\x0cB\x00\x00\x05\xde\xff\xff\xf3%\x00\x00\x07\x93\x00\x00\xfd\x90\xff\xff\xfb\xa1\xff"
        b"\xff\xfd\xa2\x00\x00\x03\xdc\x00\x00\xc0nXYZ \x00\x00\x00\x00\x00\x00o\xa0\x00\x008\xf5\x00\x00\x03"
        b"\x90XYZ \x00\x00\x00\x00\x00\x00$\x9f\x00\x00\x0f\x84\x00\x00\xb6\xc4XYZ \x00\x00\x00\x00\x00\x00b"
        b"\x97\x00\x00\xb7\x87\x00\x00\x18\xd9para\x00\x00\x00\x00\x00\x03\x00\x00\x00\x02ff\x00\x00\xf2\xa7"
        b"\x00\x00\rY\x00\x00\x13\xd0\x00\x00\n[chrm\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\xa3\xd7\x00\x00T|"
        b"\x00\x00L\xcd\x00\x00\x99\x9a\x00\x00&g\x00\x00\x0f\\mluc\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00"
        b"\x00\x0cenUS\x00\x00\x00\x08\x00\x00\x00\x1c\x00G\x00I\x00M\x00Pmluc\x00\x00\x00\x00\x00\x00\x00"
        b"\x01\x00\x00\x00\x0cenUS\x00\x00\x00\x08\x00\x00\x00\x1c\x00s\x00R\x00G\x00B\xff\xdb\x00C\x00\x01"
        b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"
        b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"
        b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\xff\xc0\x00\x0b\x08\x00\x10\x00\x10"
        b"\x01\x01\x11\x00\xff\xc4\x00\x17\x00\x00\x03\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x06\x07\x08\n\xff\xc4\x00\x1d\x10\x00\x03\x00\x03\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x05\x06\x07\x01\x04\x08\x02\x03\x13\x15\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xc4D\x0eA"
        b"\x8e\x91\xa8\xf3\xcf5N\xb5\x7f\x87k\xbc_\x96\xe3\x83]\x9c\\\xff\x00\x19f1^=:A\x98jm.\x03\x9f\x10"
        b"mW\xc2\xcbYF\xd2T\x06\xef,OXfX`^\x18\x0ez\xb4U \x91\x17\xd4\xf6\xbe\xc2\xb7\x85s:{\xa1\x8f\xec;}"
        b"\x8f-l/1|\x19\x86|\x14\xc5+j\x8cm\xf0\xde\x10\xba\x7f\xa5=\xe2\x86\xd8\x18\r\xed$o\xab2h\xbc\xad"
        b"\x8cS\x18\xba\xd8,\xb2\xa3\xbf\xd9\xd8I\x84+\x07\x9d\x1ay\x1cr\xba\x81\nu\x0f\xa7yk\xa0%5\xf2\xf4"
        b"\xf4\x9e\x8d\xe6\x19\x90+s;P\xfd\xd1\xb3\x8f\xac\xf8\x0e@5\xf5\x8f(i\xc3\x0e\xf3\xd3\xbc\xf5\xa5"
        b"\xed:\x85<$\xee\xd1@%i\xde\x1ao\xdaF$\t?Vq\xce\x92\xde\xe1\xbd\x14H\x8a'\"\x8d\xbf75\xaef\x90\xc3|"
        b"\xe8~\x82\x04\xab+3O.\xdeX&\xac\xf2t\x89\xcf\xd3\xfa\x85\xbdFu=\x8e*\xa9\xfb!\x96\xed\xfa\xe3S\xe5A"
        b"\xf2\xa8\xf5\xe8\xd7\x85\xa5\x05\t\xf8a\xff\x00\xff\xd9"
        b"\nEI\n"
    )
    content_stream = page.get_contents()
    content_stream.set_data(
        content_stream.get_data().replace(b"/Im4 Do", b"").replace(b"\nET", image_data)
    )
    page.replace_contents(content_stream)

    expected = PdfReader(RESOURCE_ROOT / "imagemagick-images.pdf").pages[3].images[0].image
    assert get_image_data(expected) == get_image_data(page.images[0].image)


def test_deprecate_inline_image_filters():
    stream = ContentStream(stream=None, pdf=None)
    stream.set_data(b"&\xa0\xbf\xcc9\x14|G#\x1f\xff\xf1\xcc9\x18\xfe\xbbX\xfc\x00@\x04")

    # The abbreviations do not work here, which is one of the reasons for the deprecation.
    stream[NameObject("/Width")] = NumberObject(16)
    stream[NameObject("/Height")] = NumberObject(16)
    stream[NameObject("/ColorSpace")] = NameObject("/DeviceGray")
    stream[NameObject("/BitsPerComponent")] = NumberObject(1)
    stream[NameObject("/Filter")] = NameObject("/CCF")
    stream[NameObject("/DecodeParams")] = ArrayObject(
        [
            DictionaryObject(
                {
                    NameObject("/K"): NumberObject(-1),
                    NameObject("/BlackIs1"): TextStringObject("false"),
                    NameObject("/Columns"): NumberObject(16),
                    NameObject("/Rows"): NumberObject(16),
                }
            )
        ]
    )

    with pytest.warns(
            expected_warning=DeprecationWarning,
            match=r"^The filter name /CCF is deprecated and will be removed in pypdf 7\.0\.0\. Use /CCITTFaxDecode instead\.$"  # noqa: E501
    ):
        decode_stream_data(stream)

    stream[NameObject("/Filter")] = NameObject("/CCITTFaxDecode")
    assert decode_stream_data(stream).startswith(b"II*")


def test_flatedecode__columns_is_zero():
    codec = FlateDecode()
    data = b"Hello World!"
    parameters = DictionaryObject({
        NameObject("/Predictor"): NumberObject(13),
        NameObject("/Columns"): NumberObject(0)
    })

    with pytest.raises(expected_exception=PdfReadError, match=r"^Expected positive number for /Columns, got 0!$"):
        codec.decode(codec.encode(data), parameters)


def test_runlengthdecode__decode_limit():
    uncompressed_size = 76 * 1024 * 1024  # 76 MB target
    runs = uncompressed_size // 128
    encoded = (b"\x81A" * runs) + b"\x80"

    with pytest.raises(expected_exception=LimitReachedError, match=r"^Limit reached while decompressing\.$"):
        RunLengthDecode.decode(encoded)

    uncompressed_size = 5 * 1024
    runs = uncompressed_size // 128
    encoded = (b"\x81A" * runs) + b"\x80"

    # Use a very low limit for this exact comparison, otherwise *pytest* takes ages to render a failure diff.
    with mock.patch("pypdf.filters.RUN_LENGTH_MAX_OUTPUT_LENGTH", uncompressed_size):
        assert RunLengthDecode.decode(encoded) == b"A" * uncompressed_size
