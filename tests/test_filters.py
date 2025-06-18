"""Test the pypdf.filters module."""
import os
import shutil
import string
import subprocess
from io import BytesIO
from itertools import product as cartesian_product
from pathlib import Path
from unittest import mock

import pytest
from PIL import Image, ImageOps

from pypdf import PdfReader
from pypdf.errors import DependencyError, DeprecationError, PdfReadError, PdfStreamError
from pypdf.filters import (
    ASCII85Decode,
    ASCIIHexDecode,
    CCITParameters,
    CCITTFaxDecode,
    CCITTParameters,
    FlateDecode,
    JBIG2Decode,
)
from pypdf.generic import (
    ArrayObject,
    ContentStream,
    DictionaryObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
)

from . import PILContext, get_data_from_url
from .test_encryption import HAS_AES
from .test_images import image_similarity

filter_inputs = (
    string.ascii_lowercase,
    string.ascii_uppercase,
    string.ascii_letters,
    string.digits,
    string.hexdigits,
    string.punctuation,
    string.whitespace,  # Add more...
)

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


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

    Predictors outside the [10, 15] range are not supported.

    This test function checks that a PdfReadError is raised when decoding with
    unsupported predictors. Once this predictor support is updated in the
    future, this test case may be removed.
    """
    codec = FlateDecode()
    predictors = (-10, -1, 0, 9, 16, 20, 100)

    for predictor, s in cartesian_product(predictors, filter_inputs):
        s = s.encode()
        with pytest.raises(PdfReadError):
            codec.decode(codec.encode(s), DictionaryObject({"/Predictor": predictor}))


@pytest.mark.parametrize("params", [ArrayObject([]), ArrayObject([{"/Predictor": 1}])])
def test_flate_decode_decompress_with_array_params(params):
    """FlateDecode decode() method works correctly with array parameters."""
    codec = FlateDecode()
    s = b""
    encoded = codec.encode(s)
    with pytest.raises(DeprecationError):
        assert codec.decode(encoded, params) == s


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


def test_ascii_hex_decode_missing_eod():
    """ASCIIHexDecode.decode() raises error when no EOD character is present."""
    # with pytest.raises(PdfStreamError) as exc:
    ASCIIHexDecode.decode("")
    # assert exc.value.args[0] == "Unexpected EOD in ASCIIHexDecode"


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
    with pytest.warns(
        DeprecationWarning,
        match="CCITParameters is deprecated and will be removed in pypdf 6.0.0. Use CCITTParameters instead",
    ):
        params = CCITParameters()
    assert params.K == 0  # zero is the default according to page 78
    assert params.group == 3


def test_ccittparameters():
    params = CCITTParameters()
    assert params.K == 0  # zero is the default according to page 78
    assert params.group == 3


@pytest.mark.parametrize(
    ("parameters", "expected_k"),
    [
        (None, 0),
        (ArrayObject([{"/K": NumberObject(1)}, {"/Columns": NumberObject(13)}]), 1),
    ],
)
def test_ccitt_get_parameters(parameters, expected_k):
    parameters = CCITTFaxDecode._get_parameters(parameters=parameters, rows=0)
    assert parameters.K == expected_k  # noqa: SIM300


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

    # This was just the result pypdf 1.27.9 returned.
    # It would be awesome if we could check if that is actually correct.
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
        [shutil.which("python"), source_file],
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
    data = get_data_from_url(name="issue-1801.png")
    assert data == images[0].data


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
    assert list(img.getdata()) == list(refimg.getdata())


@pytest.mark.enable_socket
def test_iss1787():
    """Cf issue #1787"""
    reader = PdfReader(BytesIO(get_data_from_url(name="pdf_font_garbled.pdf")))
    refimg = Image.open(BytesIO(get_data_from_url(name="watermark1.png")))
    data = reader.pages[0].images[0]
    img = Image.open(BytesIO(data.data))
    assert ".png" in data.name
    assert list(img.getdata()) == list(refimg.getdata())
    obj = data.indirect_reference.get_object()
    obj["/DecodeParms"][NameObject("/Columns")] = NumberObject(1000)
    obj.decoded_self = None
    with pytest.raises(expected_exception=PdfReadError, match="^Unsupported PNG filter 244$"):
        _ = reader.pages[0].images[0]


@pytest.mark.enable_socket
def test_tiff_predictor():
    """Decode Tiff Predictor 2 Images"""
    reader = PdfReader(BytesIO(get_data_from_url(name="tika-977609.pdf")))
    refimg = Image.open(BytesIO(get_data_from_url(name="tifimage.png")))
    data = reader.pages[0].images[0]
    img = Image.open(BytesIO(data.data))
    assert ".png" in data.name
    assert list(img.getdata()) == list(refimg.getdata())


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
def test_cmyk():
    """Decode CMYK"""
    # JPEG compression
    try:
        from Crypto.Cipher import AES  # noqa: F401, PLC0415
    except ImportError:
        return  # the file is encrypted
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


@pytest.mark.enable_socket
def test_ccitt_fax_decode__black_is_1():
    url = "https://github.com/user-attachments/files/19288881/imagemagick-CCITTFaxDecode_BlackIs1-true.pdf"
    name = "issue3193.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    other_reader = PdfReader(RESOURCE_ROOT / "imagemagick-CCITTFaxDecode.pdf")

    actual_image = reader.pages[0].images[0].image
    expected_image_inverted = other_reader.pages[0].images[0].image
    expected_pixels = list(ImageOps.invert(expected_image_inverted).getdata())
    actual_pixels = list(actual_image.getdata())
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
    actual_image = BytesIO()
    Image.frombytes(mode="1", size=(4881, 81), data=actual).save(actual_image, format="png")

    url = "https://github.com/user-attachments/assets/c5695850-c076-4255-ab72-7c86851a4a04"
    name = "issue3241.png"
    expected = get_data_from_url(url, name=name)
    assert actual_image.getvalue() == expected
    assert caplog.messages == ["Image data is not rectangular. Adding padding."]


def test_jbig2decode__binary_errors():
    with mock.patch("pypdf.filters.JBIG2DEC_BINARY", None), \
            pytest.raises(DependencyError, match="jbig2dec binary is not available."):
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
            pytest.raises(DependencyError, match="jbig2dec>=0.15 is required."):
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
    image = Image.open(BytesIO(result), formats=("PNG",))
    for x in range(5):
        for y in range(5):
            assert image.getpixel((x, y)) == (255 if x < 3 else 0), (x, y)
    assert caplog.messages == []

    # No decode_params. Completely white image.
    result = JBIG2Decode.decode(image_data)
    image = Image.open(BytesIO(result), formats=("PNG",))
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
    image = Image.open(BytesIO(result), formats=("PNG",))
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
    image = Image.open(BytesIO(result), formats=("PNG",))
    for x in range(5):
        for y in range(5):
            assert image.getpixel((x, y)) == 255, (x, y)
    assert caplog.messages == [
        "jbig2dec WARNING text region refers to no symbol dictionaries (segment 0x00000002)",
        "jbig2dec WARNING ignoring out of range symbol ID (0/0) (segment 0x00000002)"
    ]
    caplog.clear()

    # Invalid input.
    with pytest.raises(PdfStreamError, match="Unable to decode JBIG2 data. Exit code: 1"):
        JBIG2Decode.decode(b"aaaaaa")
    assert caplog.messages == [
        "jbig2dec FATAL ERROR page has no image, cannot be completed",
        "jbig2dec WARNING unable to complete page"
    ]
