"""
Tests which ensure that image extraction works properly go here.

Typically, tests in here should compare the extracted images count, names,
and/or the actual image data with the expected value.
"""

from io import BytesIO
from pathlib import Path
from typing import Union
from unittest import mock
from zipfile import ZipFile

import pytest
from PIL import Image, ImageChops, ImageDraw

from pypdf import PageObject, PdfReader, PdfWriter
from pypdf.filters import JBIG2Decode
from pypdf.generic import ContentStream, NameObject, NullObject

from . import get_data_from_url

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
SAMPLE_ROOT = PROJECT_ROOT / "sample-files"


def open_image(path: Union[Path, Image.Image, BytesIO]) -> Image.Image:
    if isinstance(path, Image.Image):
        img = path
    else:
        if isinstance(path, Path):
            assert path.exists()
        with Image.open(path) as img:
            img = (
                img.copy()
            )  # Opened image should be copied to avoid issues with file closing
    return img


def image_similarity(
    path1: Union[Path, Image.Image, BytesIO], path2: Union[Path, Image.Image, BytesIO]
) -> float:
    """
    Check image similarity.

    A value of "0" means the images are different. A value of 1 means they are
    identical. A value above 0.9 means they are almost the same.

    This can be used to ensure visual similarity.
    """
    # Open the images using Pillow
    image1 = open_image(path1)
    image2 = open_image(path2)

    # Check if the images have the same dimensions
    if image1.size != image2.size:
        return 0

    # Check if the color modes are the same
    if image1.mode != image2.mode:
        return 0

    # Calculate the Mean Squared Error (MSE)
    diff = ImageChops.difference(image1, image2)
    pixels = list(diff.getdata())

    if isinstance(pixels[0], tuple):
        mse = sum(sum((c / 255.0) ** 2 for c in p) for p in pixels) / (
            len(pixels) * len(pixels[0])
        )
    else:
        mse = sum((p / 255.0) ** 2 for p in pixels) / len(pixels)

    return 1 - mse


@pytest.mark.samples
def test_image_similarity_one():
    path_a = SAMPLE_ROOT / "018-base64-image/page-0-QuickPDFImd32aa1ab.png"
    path_b = path_a
    assert image_similarity(path_a, path_b) == 1


@pytest.mark.samples
def test_image_similarity_zero():
    path_a = SAMPLE_ROOT / "018-base64-image/page-0-QuickPDFImd32aa1ab.png"
    path_b = SAMPLE_ROOT / "009-pdflatex-geotopo/page-23-Im2.png"
    assert image_similarity(path_a, path_b) == 0


@pytest.mark.samples
def test_image_similarity_mid():
    path_a = SAMPLE_ROOT / "018-base64-image/page-0-QuickPDFImd32aa1ab.png"
    img_b = Image.open(path_a)
    draw = ImageDraw.Draw(img_b)

    # Fill the rectangle with black color
    draw.rectangle([0, 0, 100, 100], fill=(0, 0, 0))
    sim1 = image_similarity(path_a, img_b)
    assert sim1 > 0.9
    assert sim1 > 0
    assert sim1 < 1

    draw.rectangle([0, 0, 200, 200], fill=(0, 0, 0))
    sim2 = image_similarity(path_a, img_b)
    assert sim2 < sim1
    assert sim2 > 0


@pytest.mark.enable_socket
def test_image_new_property():
    name = "pdf_font_garbled.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(name=name)))
    assert reader.pages[0].images.keys() == [
        "/I0",
        "/I1",
        "/I2",
        "/I3",
        "/I4",
        "/I5",
        "/I6",
        "/I7",
        "/I8",
        "/I9",
        ["/TPL1", "/Image5"],
        ["/TPL2", "/Image53"],
        ["/TPL2", "/Image37"],
        ["/TPL2", "/Image49"],
        ["/TPL2", "/Image51"],
        ["/TPL2", "/Image39"],
        ["/TPL2", "/Image57"],
        ["/TPL2", "/Image55"],
        ["/TPL2", "/Image43"],
        ["/TPL2", "/Image30"],
        ["/TPL2", "/Image22"],
        ["/TPL2", "/Image41"],
        ["/TPL2", "/Image47"],
        ["/TPL2", "/Image45"],
        ["/TPL3", "/Image65"],
        ["/TPL3", "/Image30"],
        ["/TPL3", "/Image61"],
        ["/TPL4", "/Image30"],
        ["/TPL5", "/Image30"],
        ["/TPL6", "/Image30"],
        ["/TPL7", "/Image30"],
        ["/TPL8", "/Image30"],
        ["/TPL9", "/Image30"],
        ["/TPL10", "/Image30"],
        ["/TPL11", "/Image30"],
        ["/TPL12", "/Image30"],
    ]
    assert len(reader.pages[0].images.items()) == 36
    assert reader.pages[0].images[0].name == "I0.png"
    assert len(reader.pages[0].images[-1].data) == 15168
    assert reader.pages[0].images["/TPL1", "/Image5"].image.format == "JPEG"
    assert (
        reader.pages[0].images["/I0"].indirect_reference.get_object()
        == reader.pages[0]["/Resources"]["/XObject"]["/I0"]
    )
    list(reader.pages[0].images[0:2])
    with pytest.raises(TypeError):
        reader.pages[0].images[b"0"]
    with pytest.raises(IndexError):
        reader.pages[0].images[9999]
    # just for test coverage:
    with pytest.raises(KeyError):
        reader.pages[0]._get_image(["test"], reader.pages[0])
    assert list(PageObject(None, None).images) == []


@pytest.mark.parametrize(
    ("src", "page_index", "image_key", "expected"),
    [
        (
            SAMPLE_ROOT / "009-pdflatex-geotopo/GeoTopo.pdf",
            23,
            "/Im2",
            SAMPLE_ROOT / "009-pdflatex-geotopo/page-23-Im2.png",
        ),
        (
            SAMPLE_ROOT / "003-pdflatex-image/pdflatex-image.pdf",
            0,
            "/Im1",
            SAMPLE_ROOT / "003-pdflatex-image/page-0-Im1.jpg",
        ),
        (
            SAMPLE_ROOT / "018-base64-image/base64image.pdf",
            0,
            "/QuickPDFImd32aa1ab",
            SAMPLE_ROOT / "018-base64-image/page-0-QuickPDFImd32aa1ab.png",
        ),
        (
            SAMPLE_ROOT / "019-grayscale-image/grayscale-image.pdf",
            0,
            "/X0",
            SAMPLE_ROOT / "019-grayscale-image/page-0-X0.png",
        ),
    ],
    ids=[
        "009-pdflatex-geotopo/page-23-Im2.png",
        "003-pdflatex-image/page-0-Im1.jpg",
        "018-base64-image/page-0-QuickPDFImd32aa1ab.png",
        "019-grayscale-image/page-0-X0.png",
    ],
)
@pytest.mark.samples
def test_image_extraction(src, page_index, image_key, expected):
    reader = PdfReader(src)
    actual_image = reader.pages[page_index].images[image_key]
    if not expected.exists():
        # A little helper for test generation
        with open(f"page-{page_index}-{actual_image.name}", "wb") as fp:
            fp.write(actual_image.data)
    assert image_similarity(BytesIO(actual_image.data), expected) >= 0.99


@pytest.mark.enable_socket
@pytest.mark.timeout(30)
def test_loop_in_image_keys():
    """Cf #2077"""
    reader = PdfReader(BytesIO(get_data_from_url(name="iss2077.pdf")))
    reader.pages[0]["/Resources"]["/XObject"][NameObject("/toto")] = NullObject()
    reader.pages[0].images.keys()


@pytest.mark.enable_socket
def test_devicen_cmyk_black_only():
    """Cf #2321"""
    url = "https://github.com/py-pdf/pypdf/files/13501846/Addressing_Adversarial_Attacks.pdf"
    name = "iss2321.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    url = "https://github.com/py-pdf/pypdf/assets/4083478/cc2dabc1-86e6-4179-a8a4-2b0efea124be"
    name = "iss2321_img0.pdf"
    img = Image.open(BytesIO(get_data_from_url(url, name=name)))
    assert image_similarity(reader.pages[5].images[0].image, img) >= 0.99
    url = "https://github.com/py-pdf/pypdf/assets/4083478/6b64a949-42be-40d5-9eea-95707f350d89"
    name = "iss2321_img1.pdf"
    img = Image.open(BytesIO(get_data_from_url(url, name=name)))
    assert image_similarity(reader.pages[10].images[0].image, img) >= 0.99


@pytest.mark.enable_socket
def test_bi_in_text():
    """Cf #2456"""
    url = "https://github.com/py-pdf/pypdf/files/14322910/BI_text_with_one_image.pdf"
    name = "BI_text_with_one_image.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    assert reader.pages[0].images.keys() == ["~0~"]
    assert reader.pages[0].images[0].name == "~0~.png"


@pytest.mark.enable_socket
def test_cmyk_no_filter():
    """Cf #2522"""
    url = "https://github.com/py-pdf/pypdf/files/14614887/out3.pdf"
    name = "iss2522.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    reader.pages[0].images[0].image


@pytest.mark.enable_socket
def test_separation_1byte_to_rgb_inverted():
    """Cf #2343"""
    url = "https://github.com/py-pdf/pypdf/files/13679585/test2_P038-038.pdf"
    name = "iss2343.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    url = "https://github.com/py-pdf/pypdf/assets/4083478/b7f41897-96ef-4ea6-b165-5ef307a92b87"
    name = "iss2343.png"
    img = Image.open(BytesIO(get_data_from_url(url, name=name)))
    assert image_similarity(reader.pages[0].images[0].image, img) >= 0.99
    obj = reader.pages[0].images[0].indirect_reference.get_object()
    obj.set_data(obj.get_data() + b"\x00")
    with pytest.raises(ValueError):
        reader.pages[0].images[0]


@pytest.mark.enable_socket
def test_data_with_lf():
    """Cf #2343"""
    url = "https://github.com/py-pdf/pypdf/files/13946477/panda.pdf"
    name = "iss2343b.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    url = "https://github.com/py-pdf/pypdf/assets/4083478/1120b0cf-a67a-403f-aa1a-9a191cbc087f"
    name = "iss2343b0.png"
    img = Image.open(BytesIO(get_data_from_url(url, name=name)))
    assert image_similarity(reader.pages[8].images[9].image, img) == 1.0


@pytest.mark.enable_socket
def test_oserror():
    """Cf #2265"""
    url = "https://github.com/py-pdf/pypdf/files/13127130/Binance.discovery.responses.2.gov.uscourts.dcd.256060.140.1.pdf"
    name = "iss2265.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    reader.pages[2].images[1]
    # Due to errors in translation in pillow we may not get
    # the correct image. Therefore we cannot use `image_similarity`.


@pytest.mark.parametrize(
    ("pdf", "pdf_name", "images", "images_name", "filtr"),
    [
        (
            "https://github.com/py-pdf/pypdf/files/13127197/FTX.Claim.SC30.01072023101624File595287144.pdf",
            "iss2266a.pdf",
            "https://github.com/py-pdf/pypdf/files/14967061/iss2266a_images.zip",
            "iss2266a_images.zip",
            ((0, 0), (1, 0), (4, 0), (9, 0)),  # random pick-up to speed up test
        ),
        (
            "https://github.com/py-pdf/pypdf/files/13127242/FTX.Claim.Skybridge.Capital.30062023113350File971325116.pdf",
            "iss2266b.pdf",
            "https://github.com/py-pdf/pypdf/files/14967099/iss2266b_images.zip",
            "iss2266b_images.zip",
            ((0, 0), (1, 0), (4, 0), (9, 0)),  # random pick-up to speed up test
        ),
    ],
)
@pytest.mark.enable_socket
def test_corrupted_jpeg_iss2266(pdf, pdf_name, images, images_name, filtr):
    """
    Code to create zipfile:
    import pypdf;zipfile

    with pypdf.PdfReader("____inputfile___") as r:
     with zipfile.ZipFile("__outputzip___","w") as z:
      for p in r.pages:
       for ii,i in enumerate(p.images):
        print(i.name)
        b=BytesIO()
        i.image.save(b,"JPEG")
        z.writestr(f"image_{p.page_number}_{ii}_{i.name}",b.getbuffer())
    """
    url = pdf
    name = pdf_name
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    url = images
    name = images_name
    print(pdf_name, images_name)  # noqa: T201
    with ZipFile(BytesIO(get_data_from_url(url, name=name)), "r") as zf:
        for fn in zf.namelist():
            sp = fn.split("_")
            p, i = int(sp[1]), int(sp[2])
            if filtr is not None and (p, i) not in filtr:
                continue
            print(fn)  # noqa: T201
            img = Image.open(BytesIO(zf.read(fn)))
            assert image_similarity(reader.pages[p].images[i].image, img) >= 0.99


@pytest.mark.enable_socket
@pytest.mark.timeout(30)
def test_large_compressed_image():
    url = "https://github.com/py-pdf/pypdf/files/15306199/file_with_large_compressed_image.pdf"
    reader = PdfReader(
        BytesIO(get_data_from_url(url, name="file_with_large_compressed_image.pdf"))
    )
    list(reader.pages[0].images)


@pytest.mark.enable_socket
def test_ff_fe_starting_lut():
    """Cf issue #2660"""
    url = "https://github.com/py-pdf/pypdf/files/15385628/original_before_merge.pdf"
    name = "iss2660.pdf"
    writer = PdfWriter(BytesIO(get_data_from_url(url, name=name)))
    b = BytesIO()
    writer.write(b)
    reader = PdfReader(b)
    url = "https://github.com/py-pdf/pypdf/assets/4083478/6150700d-87fd-43a2-8695-c2c05a44838c"
    name = "iss2660.png"
    img = Image.open(BytesIO(get_data_from_url(url, name=name)))
    assert image_similarity(writer.pages[1].images[0].image, img) == 1.0
    assert image_similarity(reader.pages[1].images[0].image, img) == 1.0


@pytest.mark.enable_socket
def test_inline_image_extraction():
    """Cf #2598"""
    url = "https://github.com/py-pdf/pypdf/files/14982414/lebo102.pdf"
    name = "iss2598.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    # there is no error because images are correctly extracted
    reader.pages[1].extract_text()
    reader.pages[2].extract_text()
    reader.pages[3].extract_text()

    url = "https://github.com/py-pdf/pypdf/files/15210011/Pages.62.73.from.0560-22_WSP.Plan_July.2022_Version.1.pdf"
    name = "iss2598a.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    reader.pages[0].extract_text()
    reader.pages[1].extract_text()

    url = "https://github.com/mozilla/pdf.js/raw/master/test/pdfs/issue14256.pdf"
    name = "iss2598b.pdf"
    writer = PdfWriter(BytesIO(get_data_from_url(url, name=name)))
    url = "https://github.com/py-pdf/pypdf/assets/4083478/71bc5053-cfc7-44ba-b7be-8e2333e2c749"
    name = "iss2598b.png"
    img = Image.open(BytesIO(get_data_from_url(url, name=name)))
    for i in range(8):
        assert image_similarity(writer.pages[0].images[i].image, img) == 1
    writer.pages[0].extract_text()
    # check recalculation of inline images
    assert writer.pages[0].inline_images is not None
    writer.pages[0].merge_scaled_page(writer.pages[0], 0.25)
    assert writer.pages[0].inline_images is None
    reader = PdfReader(RESOURCE_ROOT / "imagemagick-ASCII85Decode.pdf")
    writer.pages[0].merge_page(reader.pages[0])
    assert list(writer.pages[0].images.keys()) == [
        "/Im0",
        "~0~",
        "~1~",
        "~2~",
        "~3~",
        "~4~",
        "~5~",
        "~6~",
        "~7~",
        "~8~",
        "~9~",
        "~10~",
        "~11~",
        "~12~",
        "~13~",
        "~14~",
        "~15~",
    ]

    url = "https://github.com/py-pdf/pypdf/files/15233597/bug1065245.pdf"
    name = "iss2598c.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    url = "https://github.com/py-pdf/pypdf/assets/4083478/bfb221be-11bd-46fe-8129-55a58088a4b6"
    name = "iss2598c.jpg"
    img = Image.open(BytesIO(get_data_from_url(url, name=name)))
    assert image_similarity(reader.pages[0].images[0].image, img) >= 0.99

    url = "https://github.com/py-pdf/pypdf/files/15282904/tt.pdf"
    name = "iss2598d.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    url = "https://github.com/py-pdf/pypdf/assets/4083478/1a770e1b-9ad2-4125-89ae-6069992dda23"
    name = "iss2598d.png"
    img = Image.open(BytesIO(get_data_from_url(url, name=name)))
    assert image_similarity(reader.pages[0].images[0].image, img) == 1


@pytest.mark.enable_socket
def test_extract_image_from_object(caplog):
    url = "https://github.com/py-pdf/pypdf/files/15176076/B2.pdf"
    name = "iss2613.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    image = reader.pages[0]["/Resources"]["/Pattern"]["/P1"]["/Resources"]["/XObject"][
        "/X1"
    ].decode_as_image()
    assert isinstance(image, Image.Image)
    with pytest.raises(Exception):
        co = reader.pages[0].get_contents()
        co.decode_as_image()
    assert "does not seem to be an Image" in caplog.text
    caplog.clear()
    co.indirect_reference = "for_test"
    with pytest.raises(Exception):
        co = reader.pages[0].get_contents()
        co.decode_as_image()
    assert "does not seem to be an Image" in caplog.text


@pytest.mark.enable_socket
def test_4bits_images(caplog):
    url = "https://github.com/user-attachments/files/16624406/tt.pdf"
    name = "iss2411.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    url = "https://github.com/user-attachments/assets/53058564-9a28-4e4a-818f-a6528013d7dc"
    name = "iss2411.png"
    img = Image.open(BytesIO(get_data_from_url(url, name=name)))
    assert image_similarity(reader.pages[0].images[1].image, img) == 1.0


@pytest.mark.enable_socket
def test_no_filter_with_colorspace_as_list():
    """Tests for #2998"""
    url = "https://github.com/user-attachments/files/18058571/9bf7a2e2-72c8-4ac1-b8ae-164df16c8cef.pdf"
    name = "iss2998.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))

    page = reader.pages[0]
    page.images.items()


def test_contentstream__read_inline_image__fallback_is_successful():
    stream = ContentStream(stream=None, pdf=None)
    stream.set_data(
        b"""Q
q 9.6 0 0 4.8 5523.6 1031 cm
BI
/CS /RGB
/W 2
/H 1
/BPC 8
ID \x8b\x8b\x8b\xfe\xfe\xfe
EI Q
/R413 gs
        """
    )
    page = PageObject(pdf=None)
    with mock.patch.object(page, "get_contents", return_value=stream):
        images = page._get_inline_images()
        assert list(images) == ["~0~"]
        assert images["~0~"].data == (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x02\x00\x00\x00\x01\x08\x02\x00\x00\x00{@\xe8\xdd\x00\x00\x00\x0f"
            b"IDATx\x9cc\xe8\xee\xee\xfe\xf7\xef\x1f\x00\x0e \x04\x9cpr_\x96\x00\x00\x00\x00IEND\xaeB`\x82"
        )


@pytest.mark.enable_socket
def test_inline_image_containing_ei_in_body():
    """Tests for #3107"""
    expected = """\nID ><8d>£^H<8e><8b>¢AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA¡^BêMEI E^N^^<8a>^AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA^D
<8b>²: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA5>^D
é^EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD<98>AAAAAA<8d><82>
AAAAAAAA^B
EI\nQ\n""".encode("latin1")  # noqa: E501
    url = "https://github.com/user-attachments/files/18943249/testing.pdf"
    name = "issue3107.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    writer = PdfWriter(clone_from=reader)
    for page in writer.pages:
        page.transfer_rotation_to_content()
    output = BytesIO()
    writer.write(output)
    assert expected in output.getvalue()


@pytest.mark.enable_socket
@pytest.mark.skipif(condition=not JBIG2Decode._is_binary_compatible(), reason="Requires recent jbig2dec")
def test_jbig2decode():
    url = "https://github.com/py-pdf/pypdf/files/12090692/New.Jersey.Coinbase.staking.securities.charges.2023-0606_Coinbase-Penalty-and-C-D.pdf"
    name = "jbig2.pdf"

    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    page = reader.pages[0]
    image = next(iter(page.images))
    assert image.image.size == (5138, 6630)
    assert image.image.mode == "1"
    assert image.image.format == "PNG"

    url = "https://github.com/user-attachments/assets/d6f88c80-a2e0-4ea9-b1e0-34442041d004"
    name = "jbig2.png"
    img = Image.open(BytesIO(get_data_from_url(url, name=name)))

    assert image_similarity(image.image, img) >= 0.999


@pytest.mark.enable_socket
@pytest.mark.skipif(condition=not JBIG2Decode._is_binary_compatible(), reason="Requires recent jbig2dec")
def test_jbig2decode__jbig2globals():
    url = "https://github.com/user-attachments/files/20119148/out.pdf"
    name = "jbig2_globals.pdf"

    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    page = reader.pages[0]
    image = next(iter(page.images))
    assert image.image.size == (1067, 1067)
    assert image.image.mode == "1"
    assert image.image.format == "PNG"

    url = "https://github.com/user-attachments/assets/7ac41ee3-9c13-44cf-aa74-8f106287e354"
    name = "jbig2_globals.png"
    img = Image.open(BytesIO(get_data_from_url(url, name=name)))

    # Wrong image: 0.9618265964800714
    assert image_similarity(image.image, img) >= 0.999
