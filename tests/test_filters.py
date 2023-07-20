"""Test the pypdf.filters module."""
import string
import sys
from io import BytesIO
from itertools import product as cartesian_product
from math import sqrt
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image, ImageChops

from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError
from pypdf.filters import (
    ASCII85Decode,
    ASCIIHexDecode,
    CCITParameters,
    CCITTFaxDecode,
    FlateDecode,
)
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, NumberObject

from . import get_pdf_from_url

filter_inputs = (
    # "", '', """""",
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


@pytest.mark.parametrize(
    "params", [ArrayObject([]), ArrayObject([{"/Predictor": 1}]), "a"]
)
def test_flate_decode_decompress_with_array_params(params):
    """FlateDecode decode() method works correctly with array parameters."""
    codec = FlateDecode()
    s = ""
    s = s.encode()
    encoded = codec.encode(s)
    assert codec.decode(encoded, params) == s


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (">", ""),
        (
            "6162636465666768696a6b6c6d6e6f707172737475767778797a>",
            string.ascii_lowercase,
        ),
        (
            "4142434445464748494a4b4c4d4e4f505152535455565758595a>",
            string.ascii_uppercase,
        ),
        (
            "6162636465666768696a6b6c6d6e6f707172737475767778797a4142434445464748494a4b4c4d4e4f505152535455565758595a>",
            string.ascii_letters,
        ),
        ("30313233343536373839>", string.digits),
        (
            "3  031323334353637   3839>",
            string.digits,
        ),  # Same as previous, but whitespaced
        ("30313233343536373839616263646566414243444546>", string.hexdigits),
        ("20090a0d0b0c>", string.whitespace),
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
    ],
)
def test_ascii_hex_decode_method(data, expected):
    """
    Feeds a bunch of values to ASCIIHexDecode.decode() and ensures the
    correct output is returned.

    TODO What is decode() supposed to do for such inputs as ">>", ">>>" or
    any other not terminated by ">"? (For the latter case, an exception
    is currently raised.)
    """
    assert ASCIIHexDecode.decode(data) == expected


def test_ascii_hex_decode_missing_eod():
    """ASCIIHexDecode.decode() raises error when no EOD character is present."""
    with pytest.raises(PdfStreamError) as exc:
        ASCIIHexDecode.decode("")
    assert exc.value.args[0] == "Unexpected EOD in ASCIIHexDecode"


@pytest.mark.xfail()
def test_ascii85decode_with_overflow():
    inputs = (
        v + "~>"
        for v in "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0e\x0f"
        "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a"
        "\x1b\x1c\x1d\x1e\x1fvwxy{|}~\x7f\x80\x81\x82"
        "\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d"
        "\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98"
        "\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0¡¢£¤¥¦§¨©ª«¬"
        "\xad®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇ"
    )

    for i in inputs:
        with pytest.raises(ValueError) as exc:
            ASCII85Decode.decode(i)
        assert exc.value.args[0] == ""


def test_ascii85decode_five_zero_bytes():
    """
    ASCII85Decode handles the special case of five zero bytes correctly.

    From ISO 32000 (2008) §7.4.3:

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

    assert ASCII85Decode.decode("!!!!!") == ASCII85Decode.decode("z")

    for expected, i in zip(exp_outputs, inputs):
        assert ASCII85Decode.decode(i) == expected


def test_ccitparameters():
    parms = CCITParameters()
    assert parms.K == 0  # zero is the default according to page 78
    assert parms.group == 3


@pytest.mark.parametrize(
    ("parameters", "expected_k"),
    [
        (None, 0),
        (ArrayObject([{"/K": 1}, {"/Columns": 13}]), 1),
    ],
)
def test_ccitt_get_parameters(parameters, expected_k):
    parmeters = CCITTFaxDecode._get_parameters(parameters=parameters, rows=0)
    assert parmeters.K == expected_k


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


@pytest.mark.enable_socket()
@patch("pypdf._reader.logger_warning")
def test_decompress_zlib_error(mock_logger_warning):
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/952/952445.pdf"
    name = "tika-952445.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for page in reader.pages:
        page.extract_text()
    mock_logger_warning.assert_called_with(
        "incorrect startxref pointer(3)", "pypdf._reader"
    )


@pytest.mark.enable_socket()
def test_lzw_decode_neg1():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/921/921632.pdf"
    name = "tika-921632.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    page = reader.pages[47]
    with pytest.raises(PdfReadError) as exc:
        page.extract_text()
    assert exc.value.args[0] == "Missed the stop code in LZWDecode!"


@pytest.mark.enable_socket()
def test_issue_399():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/976/976970.pdf"
    name = "tika-976970.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    reader.pages[1].extract_text()


@pytest.mark.enable_socket()
def test_image_without_imagemagic():
    with patch.dict(sys.modules):
        sys.modules["PIL"] = None
        url = "https://corpora.tika.apache.org/base/docs/govdocs1/914/914102.pdf"
        name = "tika-914102.pdf"
        data = BytesIO(get_pdf_from_url(url, name=name))
        reader = PdfReader(data, strict=True)

        for page in reader.pages:
            with pytest.raises(ImportError) as exc:
                page.images[0]
            assert exc.value.args[0] == (
                "pillow is required to do image extraction. "
                "It can be installed via 'pip install pypdf[image]'"
            )


@pytest.mark.enable_socket()
def test_issue_1737():
    url = "https://github.com/py-pdf/pypdf/files/11068604/tt1.pdf"
    name = "iss1737.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    reader.pages[0]["/Resources"]["/XObject"]["/Im0"].get_data()
    reader.pages[0]["/Resources"]["/XObject"]["/Im1"].get_data()
    reader.pages[0]["/Resources"]["/XObject"]["/Im2"].get_data()


@pytest.mark.enable_socket()
def test_pa_image_extraction():
    """
    PNG images with PA mode can be extracted.

    This is a regression test for issue #1801
    """
    url = "https://github.com/py-pdf/pypdf/files/11250359/test_img.pdf"
    name = "issue-1801.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))

    page0 = reader.pages[0]
    images = page0.images
    assert len(images) == 1
    assert images[0].name == "Im1.png"

    # Ensure visual appearence
    data = get_pdf_from_url(
        "https://user-images.githubusercontent.com/"
        "1658117/232842886-9d1b0726-3a5b-430d-8464-595d919c266c.png",
        "issue-1801.png",
    )
    assert data == images[0].data


@pytest.mark.enable_socket()
def test_1bit_image_extraction():
    """Cf issue #1814"""
    url = "https://github.com/py-pdf/pypdf/files/11336817/grimm10.pdf"
    name = "grimm10"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for p in reader.pages:
        p.images


@pytest.mark.enable_socket()
def test_png_transparency_reverse():
    """Cf issue #1599"""
    pdf_path = RESOURCE_ROOT / "labeled-edges-center-image.pdf"
    reader = PdfReader(pdf_path)
    url_png = "https://user-images.githubusercontent.com/4083478/236685544-a1940b06-fb42-4bb1-b589-1e4ad429d68e.png"
    name_png = "labeled-edges-center-image.png"
    _refimg = Image.open(
        BytesIO(get_pdf_from_url(url_png, name=name_png))
    )  # not a pdf but it works
    data = reader.pages[0].images[0]
    _img = Image.open(BytesIO(data.data))
    assert ".jp2" in data.name
    # assert list(img.getdata()) == list(refimg.getdata())


@pytest.mark.enable_socket()
def test_iss1787():
    """Cf issue #1787"""
    url = "https://github.com/py-pdf/pypdf/files/11219022/pdf_font_garbled.pdf"
    name = "pdf_font_garbled.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    url_png = "https://user-images.githubusercontent.com/4083478/236793172-09340aef-3440-4c8a-af85-a91cdad27d46.png"
    name_png = "watermark1.png"
    refimg = Image.open(
        BytesIO(get_pdf_from_url(url_png, name=name_png))
    )  # not a pdf but it works
    data = reader.pages[0].images[0]
    img = Image.open(BytesIO(data.data))
    assert ".png" in data.name
    assert list(img.getdata()) == list(refimg.getdata())
    obj = data.indirect_reference.get_object()
    obj["/DecodeParms"][NameObject("/Columns")] = NumberObject(1000)
    obj.decoded_self = None
    with pytest.raises(PdfReadError) as exc:
        reader.pages[0].images[0]
    assert exc.value.args[0] == "Image data is not rectangular"


@pytest.mark.enable_socket()
def test_tiff_predictor():
    """Decode Tiff Predictor 2 Images"""
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/977/977609.pdf"
    name = "tika-977609.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    url_png = "https://user-images.githubusercontent.com/4083478/236793166-288b4b59-dee3-49fd-a04e-410aab06199a.png"
    name_png = "tifimage.png"
    refimg = Image.open(
        BytesIO(get_pdf_from_url(url_png, name=name_png))
    )  # not a pdf but it works
    data = reader.pages[0].images[0]
    img = Image.open(BytesIO(data.data))
    assert ".png" in data.name
    assert list(img.getdata()) == list(refimg.getdata())


@pytest.mark.enable_socket()
def test_rgba():
    """Decode rgb with transparency"""
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/972/972174.pdf"
    name = "tika-972174.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    url_png = "https://user-images.githubusercontent.com/4083478/238288207-b77dd38c-34b4-4f4f-810a-bf9db7ca0414.png"
    name_png = "tika-972174_p0-im0.png"
    refimg = Image.open(
        BytesIO(get_pdf_from_url(url_png, name=name_png))
    )  # not a pdf but it works
    data = reader.pages[0].images[0]
    assert ".jp2" in data.name
    diff = ImageChops.difference(data.image, refimg)
    d = sqrt(
        sum([(a * a + b * b + c * c + d * d) for a, b, c, d in diff.getdata()])
    ) / (diff.size[0] * diff.size[1])
    assert d < 0.01


@pytest.mark.enable_socket()
def test_cmyk():
    """Decode cmyk"""
    # JPEG compression
    try:
        from Crypto.Cipher import AES  # noqa: F401
    except ImportError:
        return  # the file is encrypted
    url = "https://github.com/py-pdf/pypdf/files/11962229/DB-5368770_Vitocal_200-G.pdf"
    name = "Vitocal.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    url_png = "https://user-images.githubusercontent.com/4083478/251283945-38c5b92c-cf94-473c-bb57-a51b74fc39be.jpg"
    name_png = "VitocalImage.png"
    refimg = Image.open(
        BytesIO(get_pdf_from_url(url_png, name=name_png))
    )  # not a pdf but it works
    data = reader.pages[1].images[0]
    assert data.image.mode == "CMYK"
    assert ".jpg" in data.name
    diff = ImageChops.difference(data.image, refimg)
    d = sqrt(
        sum([(a * a + b * b + c * c + d * d) for a, b, c, d in diff.getdata()])
    ) / (diff.size[0] * diff.size[1])
    assert d < 0.01
    # deflate
    url = "https://github.com/py-pdf/pypdf/files/12078533/cmyk2.pdf"
    name = "cmyk_deflate.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    url_png = "https://github.com/py-pdf/pypdf/files/12078556/cmyk.tif.txt"
    name_png = "cmyk_deflate.tif"
    refimg = Image.open(
        BytesIO(get_pdf_from_url(url_png, name=name_png))
    )  # not a pdf but it works
    data = reader.pages[0].images[0]
    assert data.image.mode == "CMYK"
    assert ".tif" in data.name
    diff = ImageChops.difference(data.image, refimg)
    d = sqrt(
        sum([(a * a + b * b + c * c + d * d) for a, b, c, d in diff.getdata()])
    ) / (diff.size[0] * diff.size[1])
    assert d < 0.001  # lossless compression expected


@pytest.mark.enable_socket()
def test_iss1863():
    """Test doc from iss1863"""
    url = "https://github.com/py-pdf/pypdf/files/11578953/USC.EMBA.-.Pre-Season.and.Theme.I.pdf"
    name = "o1whh9b3.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for p in reader.pages:
        for i in p.images:
            i.name


@pytest.mark.enable_socket()
def test_read_images():
    url = "https://www.selbst.de/paidcontent/dl/64733/72916"
    name = "selbst.72916.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    page = reader.pages[0]
    for _ in page.images:
        pass


@pytest.mark.enable_socket()
def test_cascaded_filters_images():
    url = "https://github.com/py-pdf/pypdf/files/11845099/GeoTopo-komprimiert.pdf"
    name = "iss1912.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    # for focus, analyse the page 23
    for p in reader.pages:
        for i in p.images:
            _ = i.name, i.image


@pytest.mark.enable_socket()
def test_calrgb():
    url = "https://github.com/py-pdf/pypdf/files/12061061/tt.pdf"
    name = "calRGB.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    reader.pages[0].images[0]


@pytest.mark.enable_socket()
def test_2bits_image():
    """From #1954, test with 2bits image. TODO: 4bits also"""
    url = "https://github.com/py-pdf/pypdf/files/12050253/tt.pdf"
    name = "paid.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    url_png = "https://user-images.githubusercontent.com/4083478/253568117-ca95cc85-9dea-4145-a5e0-032f1c1aa322.png"
    name_png = "Paid.png"
    refimg = Image.open(
        BytesIO(get_pdf_from_url(url_png, name=name_png))
    )  # not a pdf but it works
    data = reader.pages[0].images[0]
    diff = ImageChops.difference(data.image, refimg)
    d = sqrt(
        sum([(a * a + b * b + c * c + d * d) for a, b, c, d in diff.getdata()])
    ) / (diff.size[0] * diff.size[1])
    assert d < 0.01


@pytest.mark.enable_socket()
def test_gray_devicen_cmyk():
    """
    Cf #1979
    Gray Image in CMYK : requiring reverse
    """
    url = "https://github.com/py-pdf/pypdf/files/12080338/example_121.pdf"
    name = "gray_cmyk.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    url_png = "https://user-images.githubusercontent.com/4083478/254545494-42df4949-1557-4f2d-acca-6be6e8de1122.png"
    name_png = "velo.png"
    refimg = Image.open(
        BytesIO(get_pdf_from_url(url_png, name=name_png))
    )  # not a pdf but it works
    data = reader.pages[0].images[0]
    assert data.image.mode == "L"
    diff = ImageChops.difference(data.image, refimg)
    d = sqrt(sum([(a * a) for a in diff.getdata()])) / (diff.size[0] * diff.size[1])
    assert d < 0.001
