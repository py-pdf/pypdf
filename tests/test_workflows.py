"""
Tests in this module behave like user code.

They don't mock/patch anything, they cover typical user needs.
"""

import binascii
import sys
from io import BytesIO
from pathlib import Path
from re import findall

import pytest
from PIL import Image, ImageChops
from PIL import __version__ as pil_version

from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.constants import PageAttributes as PG
from pypdf.errors import PdfReadError, PdfReadWarning
from pypdf.generic import (
    ArrayObject,
    ContentStream,
    DictionaryObject,
    NameObject,
    TextStringObject,
    read_object,
)

from . import PILContext, get_data_from_url, normalize_warnings

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
SAMPLE_ROOT = PROJECT_ROOT / "sample-files"

sys.path.append(str(PROJECT_ROOT))


def test_basic_features(tmp_path):
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    assert len(reader.pages) == 1

    # add page 1 from input1 to output document, unchanged
    writer.add_page(reader.pages[0])

    # add page 2 from input1, but rotated clockwise 90 degrees
    writer.add_page(reader.pages[0].rotate(90))

    # add page 3 from input1, but first add a watermark from another PDF:
    page3 = reader.pages[0]
    watermark_pdf = pdf_path
    watermark = PdfReader(watermark_pdf)
    page3.merge_page(watermark.pages[0])
    writer.add_page(page3)

    # add page 4 from input1, but crop it to half size:
    page4 = reader.pages[0]
    page4.mediabox.upper_right = (
        page4.mediabox.right / 2,
        page4.mediabox.top / 2,
    )
    del page4.mediabox
    writer.add_page(page4)

    # add some Javascript to launch the print window on opening this PDF.
    # the password dialog may prevent the print dialog from being shown,
    # comment the encryption lines, if that's the case, to try this out
    writer.add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")

    # encrypt your new PDF and add a password
    password = "secret"
    writer.encrypt(password)
    # doing it twice should not change anything
    writer.encrypt(password)

    # finally, write "output" to pypdf-output.pdf
    write_path = tmp_path / "pypdf-output.pdf"
    with open(write_path, "wb") as output_stream:
        writer.write(output_stream)


def test_dropdown_items():
    inputfile = RESOURCE_ROOT / "libreoffice-form.pdf"
    reader = PdfReader(inputfile)
    fields = reader.get_fields()
    assert "/Opt" in fields["Nationality"]


def test_pdfreader_file_load():
    """
    Test loading and parsing of a file.

    Extract text of the file and compare to expected textual output. Expected
    outcome: file loads, text matches expected.
    """
    with open(RESOURCE_ROOT / "crazyones.pdf", "rb") as inputfile:
        # Load PDF file from file
        reader = PdfReader(inputfile)
        page = reader.pages[0]

        # Retrieve the text of the PDF
        with open(RESOURCE_ROOT / "crazyones.txt", "rb") as pdftext_file:
            pdftext = pdftext_file.read()

        text = page.extract_text().encode("utf-8")

        # Compare the text of the PDF to a known source
        for expected_line, actual_line in zip(text.splitlines(), pdftext.splitlines()):
            assert expected_line == actual_line

        pdftext = pdftext.replace(b"\r\n", b"\n")  # fix for windows
        assert text == pdftext


def test_pdfreader_jpeg_image():
    """
    Test loading and parsing of a file. Extract the image of the file and
    compare to expected textual output.

    Expected outcome: file loads, image matches expected.
    """
    with open(RESOURCE_ROOT / "jpeg.pdf", "rb") as inputfile:
        # Load PDF file from file
        reader = PdfReader(inputfile)

        # Retrieve the text of the image
        with open(RESOURCE_ROOT / "jpeg.txt") as pdftext_file:
            imagetext = pdftext_file.read()

        page = reader.pages[0]
        x_object = page[PG.RESOURCES]["/XObject"].get_object()
        data = x_object["/Im4"].get_data()

        # Compare the text of the PDF to a known source
        assert binascii.hexlify(data).decode() == imagetext


def test_decrypt():
    with open(RESOURCE_ROOT / "libreoffice-writer-password.pdf", "rb") as inputfile:
        reader = PdfReader(inputfile)
        assert reader.is_encrypted is True
        reader.decrypt("openpassword")
        assert len(reader.pages) == 1
        assert reader.is_encrypted is True
        metadict = reader.metadata
        assert dict(metadict) == {
            "/CreationDate": "D:20220403203552+02'00'",
            "/Creator": "Writer",
            "/Producer": "LibreOffice 6.4",
        }


def test_text_extraction_encrypted():
    inputfile = RESOURCE_ROOT / "libreoffice-writer-password.pdf"
    reader = PdfReader(inputfile)
    assert reader.is_encrypted is True
    reader.decrypt("openpassword")
    assert (
        reader.pages[0]
        .extract_text()
        .strip()
        .startswith("Lorem ipsum dolor sit amet")
    )


@pytest.mark.parametrize("degree", [0, 90, 180, 270, 360, -90])
def test_rotate(degree):
    with open(RESOURCE_ROOT / "crazyones.pdf", "rb") as inputfile:
        reader = PdfReader(inputfile)
        page = reader.pages[0]
        page.rotate(degree)


def test_rotate_45():
    with open(RESOURCE_ROOT / "crazyones.pdf", "rb") as inputfile:
        reader = PdfReader(inputfile)
        page = reader.pages[0]
        with pytest.raises(ValueError) as exc:
            page.rotate(45)
        assert exc.value.args[0] == "Rotation angle must be a multiple of 90"


@pytest.mark.enable_socket
@pytest.mark.slow
@pytest.mark.parametrize(
    ("enable", "url", "pages"),
    [
        (True, "https://arxiv.org/pdf/2201.00214.pdf", [0, 1, 5, 10]),
        (
            True,
            "https://github.com/py-pdf/sample-files/raw/main/009-pdflatex-geotopo/GeoTopo.pdf",
            [0, 1, 5, 10],
        ),
        (True, "https://arxiv.org/pdf/2201.00151.pdf", [0, 1, 5, 10]),
        (True, "https://arxiv.org/pdf/1707.09725.pdf", [0, 1, 5, 10]),
        (True, "https://arxiv.org/pdf/2201.00021.pdf", [0, 1, 5, 8]),
        (True, "https://arxiv.org/pdf/2201.00037.pdf", [0, 1, 5, 10]),
        (True, "https://arxiv.org/pdf/2201.00069.pdf", [0, 1, 5, 10]),
        (True, "https://arxiv.org/pdf/2201.00178.pdf", [0, 1, 5, 10]),
        (True, "https://arxiv.org/pdf/2201.00201.pdf", [0, 1, 5, 8]),
        (True, "https://arxiv.org/pdf/1602.06541.pdf", [0, 1, 5, 10]),
        (True, "https://arxiv.org/pdf/2201.00200.pdf", [0, 1, 5, 6]),
        (True, "https://arxiv.org/pdf/2201.00022.pdf", [0, 1, 5, 10]),
        (True, "https://arxiv.org/pdf/2201.00029.pdf", [0, 1, 6, 10]),
        # #1145
        (True, "https://github.com/py-pdf/pypdf/files/9174594/2017.pdf", [0]),
        # #1145, remaining issue (empty arguments for FlateEncoding)
        (
            True,
            "https://github.com/py-pdf/pypdf/files/9175966/2015._pb_decode_pg0.pdf",
            [0],
        ),
        # 6 instead of 5: as there is an issue in page 5 (missing objects)
        # and too complex to handle the warning without hiding real regressions
        (True, "https://arxiv.org/pdf/1601.03642.pdf", [0, 1, 5, 7]),
        (
            True,
            "https://github.com/py-pdf/pypdf/files/3796761/17343_2008_Order_09-Jan-2019.pdf",
            [0, 1],
        ),
        (
            True,
            "https://github.com/py-pdf/pypdf/files/8884471/ssi_manwaring.pdf",
            [0, 1],
        ),
        (True, "https://github.com/py-pdf/pypdf/files/8884469/999092.pdf", [0, 1]),
        (
            True,
            "file://" + str(RESOURCE_ROOT / "test Orient.pdf"),
            [0],
        ),  # TODO: preparation of text orientation validation
        (
            True,
            "https://github.com/py-pdf/pypdf/files/8884470/fdocuments.in_sweet-fundamentals-of-crystallography.pdf",
            [0, 1, 34, 35, 36, 118, 119, 120, 121],
        ),
        (True, "https://github.com/py-pdf/pypdf/files/8884493/998167.pdf", [0]),
        (
            True,
            "https://github.com/user-attachments/files/18382039/971703.pdf",
            [0, 1, 5, 8, 14],
        ),
        (  # faulty PDF, wrongly linearized and with 2 trailer, second with /Root
            True,
            "https://github.com/user-attachments/files/18382034/989691.pdf",
            [0],
        ),
    ],
)
def test_extract_textbench(enable, url, pages):
    if not enable:
        return
    print_result = False
    try:
        reader = PdfReader(BytesIO(get_data_from_url(url, url.split("/")[-1])))
        for page_number in pages:
            if print_result:
                print(f"**************** {url} / page {page_number} ****************")
            rst = reader.pages[page_number].extract_text()
            if print_result:
                print(f"{rst}\n*****************************\n")
    except PdfReadWarning:
        pass


def test_transform_compress_identical_objects():
    reader = PdfReader(RESOURCE_ROOT / "two-different-pages.pdf")
    writer = PdfWriter()

    for page in reader.pages:
        op = Transformation().scale(sx=0.8, sy=0.8)
        page.add_transformation(op)
        writer.add_page(page)
    writer.compress_identical_objects()
    bytes_out = BytesIO()
    writer.write(bytes_out)
    result_reader = PdfReader(bytes_out)
    pg1_text = result_reader.pages[0].extract_text()
    pg2_text = result_reader.pages[1].extract_text()
    assert pg1_text.strip() == "1"
    assert pg2_text.strip() == "2"


@pytest.mark.slow
def test_orientations():
    p = PdfReader(RESOURCE_ROOT / "test Orient.pdf").pages[0]
    p.extract_text("", "")
    p.extract_text("", "", 0)
    p.extract_text("", "", 0, 200)
    p.extract_text()
    assert findall("\\((.)\\)", p.extract_text()) == ["T", "B", "L", "R"]
    with pytest.raises(Exception):
        p.extract_text(None)
    p.extract_text("", 0)
    with pytest.raises(Exception):
        p.extract_text("", "", None)
    with pytest.raises(Exception):
        p.extract_text("", "", 0, "")
    with pytest.raises(Exception):
        p.extract_text(0, "")

    p.extract_text(0, 0)
    p.extract_text(orientations=0)

    for req, rst in (
        (0, ["T"]),
        (90, ["L"]),
        (180, ["B"]),
        (270, ["R"]),
        ((0,), ["T"]),
        ((0, 180), ["T", "B"]),
        ((45,), []),
    ):
        assert (
            findall("\\((.)\\)", p.extract_text(req)) == rst
        ), f"extract_text({req}) => {rst}"


@pytest.mark.samples
@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("base_path", "overlay_path"),
    [
        (
            "resources/crazyones.pdf",
            "sample-files/013-reportlab-overlay/reportlab-overlay.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381707/tika-935981.pdf",
            "sample-files/013-reportlab-overlay/reportlab-overlay.pdf",
        ),
    ],
)
def test_overlay(pdf_file_path, base_path, overlay_path):
    if base_path.startswith("http"):
        base_path = BytesIO(get_data_from_url(base_path, name="tika-935981.pdf"))
    else:
        base_path = PROJECT_ROOT / base_path
    reader = PdfReader(base_path)
    writer = PdfWriter()

    reader_overlay = PdfReader(PROJECT_ROOT / overlay_path)
    overlay = reader_overlay.pages[0]

    for page in reader.pages:
        page.merge_page(overlay)
        writer.add_page(page)
    with open(pdf_file_path, "wb") as fp:
        writer.write(fp)


@pytest.mark.enable_socket
@pytest.mark.slow
@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://github.com/user-attachments/files/18381697/tika-924546.pdf",
            "tika-924546.pdf",
        )
    ],
)
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_merge_with_warning(tmp_path, url, name):
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data)
    merger = PdfWriter()
    merger.append(reader)
    # This could actually be a performance bottleneck:
    merger.write(tmp_path / "tmp.merged.pdf")


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://github.com/user-attachments/files/18381757/tika-980613.pdf",
            "tika-980613.pdf",
        )
    ],
)
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_merge(tmp_path, url, name):
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data)
    merger = PdfWriter()
    merger.append(reader)
    merger.write(tmp_path / "tmp.merged.pdf")


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name", "expected_metadata"),
    [
        (
            "https://github.com/user-attachments/files/18381708/tika-935996.pdf",
            "tika-935996.pdf",
            {
                "/Author": "Unknown",
                "/CreationDate": "Thursday, May 06, 1999 3:56:54 PM",
                "/Creator": r"C:\DEB\6338",
                "/Keywords": "",
                "/Producer": "Acrobat PDFWriter 3.02 for Windows",
                "/Subject": "",
                "/Title": r"C:\DEB\6338-6R.PDF",
            },
        )
    ],
)
def test_get_metadata(url, name, expected_metadata):
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data)
    data = reader.metadata
    assert expected_metadata == data


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name", "strict", "exception"),
    [
        (
            "https://github.com/user-attachments/files/16624503/tika-938702.pdf",
            "tika-938702.pdf",
            False,
            None,  # iss #1090 is now fixed
        ),
        (
            "https://github.com/user-attachments/files/18381715/tika-942358.pdf",
            "tika-942358.pdf",
            False,
            None,
        ),
        (
            "https://github.com/user-attachments/files/18381684/tika-911260.pdf",
            "tika-911260.pdf",
            False,
            None,
        ),
        (
            "https://github.com/user-attachments/files/18381766/tika-992472.pdf",
            "tika-992472.pdf",
            False,
            None,
        ),
        (
            "https://github.com/user-attachments/files/18381756/tika-978477.pdf",
            "tika-978477.pdf",
            False,
            None,
        ),
        (
            "https://github.com/user-attachments/files/18381731/tika-960317.pdf",
            "tika-960317.pdf",
            False,
            None,
        ),
        (
            "https://github.com/user-attachments/files/18381701/tika-930513.pdf",
            "tika-930513.pdf",
            False,
            None,
        ),
        (
            "https://github.com/user-attachments/files/18381691/tika-918113.pdf",
            "tika-918113.pdf",
            True,
            None,
        ),
        (
            "https://github.com/user-attachments/files/18381711/tika-940704.pdf",
            "tika-940704.pdf",
            True,
            None,
        ),
        (
            "https://github.com/user-attachments/files/18381752/tika-976488.pdf",
            "tika-976488.pdf",
            True,
            None,
        ),
        (
            "https://github.com/user-attachments/files/18381716/tika-948176.pdf",
            "tika-948176.pdf",
            True,
            None,
        ),
    ],
)
def test_extract_text(url, name, strict, exception):
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data, strict=strict)
    if not exception:
        for page in reader.pages:
            page.extract_text()
    else:
        exc, exc_text = exception
        with pytest.raises(exc) as ex_info:
            for page in reader.pages:
                page.extract_text()
        assert ex_info.value.args[0] == exc_text


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://github.com/user-attachments/files/18381710/tika-938702.pdf",
            "tika-938702.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381725/tika-957304.pdf",
            "tika-957304.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381690/tika-915194.pdf",
            "tika-915194.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381717/tika-950337.pdf",
            "tika-950337.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381734/tika-962292.pdf",
            "tika-962292.pdf",
        ),
    ],
)
def test_compress_raised(url, name):
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    # no more error since iss #1090 fix
    for page in writer.pages:
        page.compress_content_streams()


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://github.com/user-attachments/files/18381733/tika-961883.pdf",
            "tika-961883.pdf",
        ),
    ],
)
def test_get_fields_warns(tmp_path, caplog, url, name):
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data)
    write_path = tmp_path / "tmp.txt"
    with open(write_path, "w") as fp:
        retrieved_fields = reader.get_fields(fileobj=fp)

    assert retrieved_fields == {}
    assert normalize_warnings(caplog.text) == [
        "Ignoring wrong pointing object 1 65536 (offset 0)",
        "Ignoring wrong pointing object 2 65536 (offset 0)",
        "Object 2 0 not defined.",
    ]


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://github.com/user-attachments/files/18381713/tika-942050.pdf",
            "tika-942050.pdf",
        ),
    ],
)
def test_get_fields_no_warning(tmp_path, url, name):
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data)
    write_path = tmp_path / "tmp.txt"
    with open(write_path, "w") as fp:
        retrieved_fields = reader.get_fields(fileobj=fp)

    assert len(retrieved_fields) == 10


@pytest.mark.enable_socket
def test_scale_rectangle_indirect_object():
    url = "https://github.com/user-attachments/files/18381778/tika-999944.pdf"
    name = "tika-999944.pdf"
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data)

    for page in reader.pages:
        page.scale(sx=2, sy=3)


def test_merge_output(caplog):
    # Arrange
    base = RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf"
    crazy = RESOURCE_ROOT / "crazyones.pdf"
    expected = RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR-crazyones-merged.pdf"

    # Act
    merger = PdfWriter()
    merger.append(base)
    merger.merge(1, crazy)
    stream = BytesIO()
    merger.write(stream)

    # Assert
    stream.seek(0)
    actual = stream.read()
    with open(expected, "rb") as fp:
        expected_data = fp.read()
    if actual != expected_data:
        # See https://github.com/pytest-dev/pytest/issues/9124
        pytest.fail(
            f"len(actual) = {len(actual):,} vs len(expected) = {len(expected_data):,}"
        )

    # Cleanup
    merger.close()


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://github.com/user-attachments/files/18381767/tika-994636.pdf",
            "tika-994636.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381719/tika-952133.pdf",
            "tika-952133.pdf",
        ),
        (  # JPXDecode
            "https://github.com/user-attachments/files/18381688/tika-914568.pdf",
            "tika-914568.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381718/tika-952016.pdf",
            "tika-952016.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18382223/965118.pdf",
            "tika-965118.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381729/tika-959184.pdf",
            "tika-959184.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381727/tika-958496.pdf",
            "tika-958496.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381744/tika-972174.pdf",
            "tika-972174.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381745/tika-972243.pdf",
            "tika-972243.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381743/tika-969502.pdf",
            "tika-969502.pdf",
        ),
        ("https://arxiv.org/pdf/2201.00214.pdf", "arxiv-2201.00214.pdf"),
    ],
)
def test_image_extraction(url, name):
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data)

    images_extracted = []
    root = Path("extracted-images")
    if not root.exists():
        root.mkdir()

    with PILContext():
        for page in reader.pages:
            for image in page.images:
                filename = root / image.name
                with open(filename, "wb") as img:
                    img.write(image.data)
                images_extracted.append(filename)

    # Cleanup
    do_cleanup = True  # set this to False for manual inspection
    if do_cleanup:
        for filepath in images_extracted:
            if Path(filepath).exists():
                Path(filepath).unlink()


@pytest.mark.enable_socket
def test_image_extraction_strict():
    # Emits log messages
    url = "https://github.com/user-attachments/files/18381687/tika-914102.pdf"
    name = "tika-914102.pdf"
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data, strict=True)

    images_extracted = []
    root = Path("extracted-images")
    if not root.exists():
        root.mkdir()

    for page in reader.pages:
        for image in page.images:
            filename = root / image.name
            with open(filename, "wb") as fp:
                fp.write(image.data)
            images_extracted.append(filename)

    # Cleanup
    do_cleanup = True  # set this to False for manual inspection
    if do_cleanup:
        for filepath in images_extracted:
            if Path(filepath).exists():
                Path(filepath).unlink()


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://github.com/user-attachments/files/18381754/tika-977609.pdf",
            "tika-977609.pdf",
        ),
    ],
)
def test_image_extraction2(url, name):
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data)

    images_extracted = []
    root = Path("extracted-images")
    if not root.exists():
        root.mkdir()

    for page in reader.pages:
        for image in page.images:
            filename = root / image.name
            with open(filename, "wb") as img:
                img.write(image.data)
            images_extracted.append(filename)

    # Cleanup
    do_cleanup = True  # set this to False for manual inspection
    if do_cleanup:
        for filepath in images_extracted:
            if Path(filepath).exists():
                Path(filepath).unlink()


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://github.com/user-attachments/files/18381692/tika-918137.pdf",
            "tika-918137.pdf",
        ),
        (
            "https://unglueit-files.s3.amazonaws.com/ebf/7552c42e9280b4476e59e77acc0bc812.pdf",
            "7552c42e9280b4476e59e77acc0bc812.pdf",
        ),
    ],
)
def test_get_outline(url, name):
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data)
    reader.outline


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://github.com/user-attachments/files/18381707/tika-935981.pdf",
            "tika-935981.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381709/tika-937334.pdf",
            "tika-937334.pdf",
        ),
    ],
)
def test_get_xfa(url, name):
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data)
    reader.xfa


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name", "strict"),
    [
        (
            "https://github.com/user-attachments/files/18381765/tika-988698.pdf",
            "tika-988698.pdf",
            False,
        ),
        (
            "https://github.com/user-attachments/files/18382162/914133.pdf",
            "tika-914133.pdf",
            False,
        ),
        (
            "https://github.com/user-attachments/files/18381685/tika-912552.pdf",
            "tika-912552.pdf",
            False,
        ),
        (
            "https://github.com/user-attachments/files/18381687/tika-914102.pdf",
            "tika-914102.pdf",
            True,
        ),
    ],
)
def test_get_fonts(url, name, strict):
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data, strict=strict)
    for page in reader.pages:
        page._get_fonts()


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name", "strict"),
    [
        (
            "https://github.com/user-attachments/files/18382060/tika-942303.pdf",
            "tika-942303.pdf",
            True,
        ),
        (
            "https://github.com/user-attachments/files/18381707/tika-935981.pdf",
            "tika-935981.pdf",
            True,
        ),
        (
            "https://github.com/user-attachments/files/18381738/tika-967399.pdf",
            "tika-967399.pdf",
            True,
        ),
        (
            "https://github.com/user-attachments/files/18381707/tika-935981.pdf",
            "tika-935981.pdf",
            False,
        ),
    ],
)
def test_get_xmp(url, name, strict):
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data, strict=strict)
    xmp_info = reader.xmp_metadata
    if xmp_info:
        xmp_info.dc_contributor
        xmp_info.dc_coverage
        xmp_info.dc_creator
        xmp_info.dc_date
        xmp_info.dc_description
        xmp_info.dc_format
        xmp_info.dc_identifier
        xmp_info.dc_language
        xmp_info.dc_publisher
        xmp_info.dc_relation
        xmp_info.dc_rights
        xmp_info.dc_source
        xmp_info.dc_subject
        xmp_info.dc_title
        xmp_info.dc_type
        xmp_info.pdf_keywords
        xmp_info.pdf_pdfversion
        xmp_info.pdf_producer
        xmp_info.xmp_create_date
        xmp_info.xmp_modify_date
        xmp_info.xmp_metadata_date
        xmp_info.xmp_creator_tool
        xmp_info.xmpmm_document_id
        xmp_info.xmpmm_instance_id
        xmp_info.custom_properties


@pytest.mark.enable_socket
def test_tounicode_is_identity():
    url = "https://github.com/py-pdf/pypdf/files/9998335/FP_Thesis.pdf"
    name = "FP_Thesis.pdf"
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data, strict=False)
    reader.pages[0].extract_text()


@pytest.mark.enable_socket
def test_append_forms():
    # from #1538
    writer = PdfWriter()

    url = "https://github.com/py-pdf/pypdf/files/10367412/pdfa.pdf"
    name = "form_a.pdf"
    reader1 = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    reader1.add_form_topname("form_a")
    writer.append(reader1)

    url = "https://github.com/py-pdf/pypdf/files/10367413/pdfb.pdf"
    name = "form_b.pdf"
    reader2 = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    reader2.add_form_topname("form_b")
    writer.append(reader2)

    b = BytesIO()
    writer.write(b)
    reader = PdfReader(b)
    assert len(reader.get_form_text_fields()) == len(
        reader1.get_form_text_fields()
    ) + len(reader2.get_form_text_fields())


@pytest.mark.enable_socket
def test_extra_test_iss1541():
    url = "https://github.com/py-pdf/pypdf/files/10418158/tst_iss1541.pdf"
    name = "tst_iss1541.pdf"
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data, strict=False)
    reader.pages[0].extract_text()

    cs = ContentStream(reader.pages[0]["/Contents"], None, None)
    cs.operations.insert(-1, ([], b"EMC"))
    stream = BytesIO()
    cs.write_to_stream(stream)
    stream.seek(0)
    ContentStream(read_object(stream, None, None), None, None).operations

    cs = ContentStream(reader.pages[0]["/Contents"], None, None)
    cs.operations.insert(-1, ([], b"E!C"))
    stream = BytesIO()
    cs.write_to_stream(stream)
    stream.seek(0)
    ContentStream(read_object(stream, None, None), None, None).operations

    b = BytesIO(data.getbuffer())
    reader = PdfReader(
        BytesIO(bytes(b.getbuffer()).replace(b"EI \n", b"E! \n")), strict=False
    )
    with pytest.raises(PdfReadError) as exc:
        reader.pages[0].extract_text()
    assert exc.value.args[0] == "Unexpected end of stream"


@pytest.mark.enable_socket
def test_fields_returning_stream():
    """This problem was reported in #424"""
    url = "https://github.com/mstamy2/PyPDF2/files/1948267/Simple.form.pdf"
    name = "tst_iss424.pdf"
    data = BytesIO(get_data_from_url(url, name=name))
    reader = PdfReader(data, strict=False)
    assert "BtchIssQATit_time" in reader.get_form_text_fields()["TimeStampData"]


def test_replace_image(tmp_path):
    writer = PdfWriter(clone_from=RESOURCE_ROOT / "labeled-edges-center-image.pdf")
    reader = PdfReader(RESOURCE_ROOT / "jpeg.pdf")
    img = reader.pages[0].images[0].image
    if int(pil_version.split(".")[0]) < 9:
        img = img.convert("RGB")
    writer.pages[0].images[0].replace(img)
    b = BytesIO()
    writer.write(b)
    reader2 = PdfReader(b)
    if int(pil_version.split(".")[0]) >= 9:
        assert reader2.pages[0].images[0].image.mode == "RGBA"
    # very simple image distance evaluation
    diff = ImageChops.difference(reader2.pages[0].images[0].image, img)
    d = sum(diff.convert("L").getdata()) / (diff.size[0] * diff.size[1])
    assert d < 1.5
    img = img.convert("RGB")  # quality does not apply to RGBA/JP2
    writer.pages[0].images[0].replace(img, quality=20)
    diff = ImageChops.difference(writer.pages[0].images[0].image, img)
    d1 = sum(diff.convert("L").getdata()) / (diff.size[0] * diff.size[1])
    assert d1 > d
    # extra tests for coverage
    with pytest.raises(TypeError) as exc:
        reader.pages[0].images[0].replace(img)
    assert exc.value.args[0] == "Cannot update an image not belonging to a PdfWriter."
    i = writer.pages[0].images[0]
    with pytest.raises(TypeError) as exc:
        i.replace(reader.pages[0].images[0])  # missing .image
    assert exc.value.args[0] == "new_image shall be a PIL Image"
    i.indirect_reference = None  # to behave like an inline image
    with pytest.raises(TypeError) as exc:
        i.replace(reader.pages[0].images[0].image)
    assert exc.value.args[0] == "Cannot update an inline image."

    import pypdf  # noqa: PLC0415

    try:
        pypdf._page.pil_not_imported = True
        with pytest.raises(ImportError) as exc:
            i.replace(reader.pages[0].images[0].image)
    finally:
        pypdf._page.pil_not_imported = False


@pytest.mark.enable_socket
def test_inline_images():
    """This problem was reported in #424"""
    url = "https://arxiv.org/pdf/2201.00151.pdf"
    name = "2201.00151.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    url = "https://github.com/py-pdf/pypdf/assets/4083478/28e8b87c-be2c-40d9-9c86-15c7819021bf"
    name = "inline4.png"
    img_ref = Image.open(BytesIO(get_data_from_url(url, name=name)))
    assert list(reader.pages[1].images[4].image.getdata()) == list(img_ref.getdata())
    with pytest.raises(KeyError):
        reader.pages[0].images["~999~"]
    del reader.pages[1]["/Resources"]["/ColorSpace"]["/R124"]
    reader.pages[1].inline_images = None  # to force recalculation
    with pytest.raises(PdfReadError):
        reader.pages[1].images["~1~"]

    co = reader.pages[0].get_contents()
    co.operations.append(([], b"BI"))
    reader.pages[0][NameObject("/Contents")] = co
    reader.pages[0].images.keys()

    with pytest.raises(TypeError) as exc:
        reader.pages[0].images[0].replace(img_ref)
    assert exc.value.args[0] == "Cannot update an inline image."

    _a = {}
    for x, y in reader.pages[2].images[0:-2].items():
        _a[x] = y  # noqa: PERF403  # Testing code and easier to read this way.
    with pytest.raises(KeyError) as exc:
        reader.pages[2]._get_image(("test",))

    url = "https://github.com/py-pdf/pypdf/files/15233597/bug1065245.pdf"
    name = "iss2598c.pdf"  # test data also used in test_images.py/test_inline_image_extraction()
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    assert len(reader.pages[0].images) == 3


@pytest.mark.enable_socket
def test_issue1899():
    url = "https://github.com/py-pdf/pypdf/files/11801077/lv2018tconv.pdf"
    name = "lv2018tconv.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    for i, page in enumerate(reader.pages):
        print(i)
        page.extract_text()


@pytest.mark.enable_socket
def test_cr_with_cm_operation():
    """Issue #2138"""
    url = "https://github.com/py-pdf/pypdf/files/12483807/AEO.1172.pdf"
    name = "iss2138.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    assert (
        """STATUS: FNL
STYLE: 1172 1172 KNIT SHORTIE SUMMER-B 2023
Company: AMERICAN EAGLE OUTFITTERS
Division / Dept: 50 / 170
Season: SUMMER-B 2023"""
        in reader.pages[0].extract_text()
    )
    # currently there is still a white space on last line missing
    # so we can not do a full comparison.


def remove_trailing_whitespace(text: str) -> str:
    text = text.strip()
    return "\n".join(line.rstrip() for line in text.splitlines())


@pytest.mark.samples
@pytest.mark.parametrize(
    ("pdf_path", "expected_path"),
    [
        (
            SAMPLE_ROOT / "026-latex-multicolumn/multicolumn.pdf",
            RESOURCE_ROOT / "multicolumn-lorem-ipsum.txt",
        ),
        (
            SAMPLE_ROOT / "010-pdflatex-forms/pdflatex-forms.pdf",
            RESOURCE_ROOT / "010-pdflatex-forms.txt",
        ),
    ],
)
def test_text_extraction_layout_mode(pdf_path, expected_path):
    reader = PdfReader(pdf_path)
    actual = reader.pages[0].extract_text(extraction_mode="layout")
    expected = expected_path.read_text(encoding="utf-8")
    # We don't care about trailing whitespace
    assert remove_trailing_whitespace(actual) == remove_trailing_whitespace(expected)


@pytest.mark.enable_socket
def test_layout_mode_space_vertically():
    reader = PdfReader(BytesIO(get_data_from_url(name="iss2138.pdf")))
    # remove automatically added final newline
    expected = (
        (RESOURCE_ROOT / "AEO.1172.layout.txt").read_text(encoding="utf-8").rstrip()
    )
    assert expected == reader.pages[0].extract_text(
        extraction_mode="layout", layout_mode_space_vertically=False
    )


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("rotation", "strip_rotated"), [(90, True), (180, False), (270, True)]
)
def test_layout_mode_rotations(rotation, strip_rotated):
    reader = PdfReader(BytesIO(get_data_from_url(name="iss2138.pdf")))
    rotated_page = reader.pages[0].rotate(rotation)
    rotated_page.transfer_rotation_to_content()
    expected = ""
    if not strip_rotated:
        expected = (
            (RESOURCE_ROOT / "AEO.1172.layout.rot180.txt")
            .read_text(encoding="utf-8")
            .rstrip()
        )  # remove automatically added final newline
    assert expected == rotated_page.extract_text(
        extraction_mode="layout",
        layout_mode_space_vertically=False,
        layout_mode_strip_rotated=strip_rotated,
    )


def test_text_extraction_invalid_mode():
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    with pytest.raises(ValueError, match="Invalid text extraction mode"):
        reader.pages[0].extract_text(extraction_mode="foo")  # type: ignore


@pytest.mark.enable_socket
def test_get_page_showing_field():
    """
    Uses testfile from #2452 in order to get fields on multiple pages,
        choices boxes,...
    """
    url = "https://github.com/py-pdf/pypdf/files/14031491/Form_Structure_v50.pdf"
    name = "iss2452.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name)))
    writer = PdfWriter(clone_from=reader)

    # validate with Field:  only works on Reader (no get_fields on writer yet)
    fld = reader.get_fields()
    assert [
        p.page_number for p in reader.get_pages_showing_field(fld["FormVersion"])
    ] == [0]

    # validate with dictionary object
    # NRCategory field is a radio box
    assert [
        p.page_number
        for p in reader.get_pages_showing_field(
            reader.trailer["/Root"]["/AcroForm"]["/Fields"][8].get_object()
        )
    ] == [0, 0, 0, 0, 0]
    assert [
        p.page_number
        for p in writer.get_pages_showing_field(
            writer._root_object["/AcroForm"]["/Fields"][8].get_object()
        )
    ] == [0, 0, 0, 0, 0]

    # validate with IndirectObject
    # SiteID field is a textbox on multiple pages
    assert [
        p.page_number
        for p in reader.get_pages_showing_field(
            reader.trailer["/Root"]["/AcroForm"]["/Fields"][99]
        )
    ] == [0, 1]
    assert [
        p.page_number
        for p in writer.get_pages_showing_field(
            writer._root_object["/AcroForm"]["/Fields"][99]
        )
    ] == [0, 1]
    # test directly on the widget:
    assert [
        p.page_number
        for p in reader.get_pages_showing_field(
            reader.trailer["/Root"]["/AcroForm"]["/Fields"][99]["/Kids"][1]
        )
    ] == [1]
    assert [
        p.page_number
        for p in writer.get_pages_showing_field(
            writer._root_object["/AcroForm"]["/Fields"][99]["/Kids"][1]
        )
    ] == [1]

    # Exceptions:
    # Invalid Object
    with pytest.raises(ValueError) as exc:
        reader.get_pages_showing_field(None)
    with pytest.raises(ValueError) as exc:
        writer.get_pages_showing_field(None)
    assert "Field type is invalid" in exc.value.args[0]

    # Damage Field
    del reader.trailer["/Root"]["/AcroForm"]["/Fields"][1].get_object()["/FT"]
    del writer._root_object["/AcroForm"]["/Fields"][1].get_object()["/FT"]
    with pytest.raises(ValueError) as exc:
        reader.get_pages_showing_field(
            reader.trailer["/Root"]["/AcroForm"]["/Fields"][1]
        )
    with pytest.raises(ValueError) as exc:
        writer.get_pages_showing_field(writer._root_object["/AcroForm"]["/Fields"][1])
    assert "Field is not valid" in exc.value.args[0]

    # missing Parent in field
    del reader.trailer["/Root"]["/AcroForm"]["/Fields"][99]["/Kids"][1].get_object()[
        "/Parent"
    ]
    del writer._root_object["/AcroForm"]["/Fields"][99]["/Kids"][1].get_object()[
        "/Parent"
    ]
    with pytest.raises(ValueError) as exc:
        reader.get_pages_showing_field(
            reader.trailer["/Root"]["/AcroForm"]["/Fields"][1]
        )
    with pytest.raises(ValueError) as exc:
        writer.get_pages_showing_field(writer._root_object["/AcroForm"]["/Fields"][1])

    # remove "/P" (optional)
    del reader.trailer["/Root"]["/AcroForm"]["/Fields"][8]["/Kids"][1].get_object()[
        "/P"
    ]
    del writer._root_object["/AcroForm"]["/Fields"][8]["/Kids"][1].get_object()["/P"]
    assert [
        p.page_number
        for p in reader.get_pages_showing_field(
            reader.trailer["/Root"]["/AcroForm"]["/Fields"][8]["/Kids"][1]
        )
    ] == [0]
    assert [
        p.page_number
        for p in writer.get_pages_showing_field(
            writer._root_object["/AcroForm"]["/Fields"][8]["/Kids"][1]
        )
    ] == [0]
    assert [
        p.page_number
        for p in reader.get_pages_showing_field(
            reader.trailer["/Root"]["/AcroForm"]["/Fields"][8].get_object()
        )
    ] == [0, 0, 0, 0, 0]
    assert [
        p.page_number
        for p in writer.get_pages_showing_field(
            writer._root_object["/AcroForm"]["/Fields"][8].get_object()
        )
    ] == [0, 0, 0, 0, 0]

    # Grouping fields
    reader.trailer["/Root"]["/AcroForm"]["/Fields"][-1].get_object()[
        NameObject("/Kids")
    ] = ArrayObject([reader.trailer["/Root"]["/AcroForm"]["/Fields"][0]])
    del reader.trailer["/Root"]["/AcroForm"]["/Fields"][-1].get_object()["/T"]
    del reader.trailer["/Root"]["/AcroForm"]["/Fields"][-1].get_object()["/P"]
    del reader.trailer["/Root"]["/AcroForm"]["/Fields"][-1].get_object()["/Subtype"]
    writer._root_object["/AcroForm"]["/Fields"].append(
        writer._add_object(
            DictionaryObject(
                {
                    NameObject("/T"): TextStringObject("grouping"),
                    NameObject("/FT"): NameObject("/Tx"),
                    NameObject("/Kids"): ArrayObject(
                        [reader.trailer["/Root"]["/AcroForm"]["/Fields"][0]]
                    ),
                }
            )
        )
    )
    assert [
        p.page_number
        for p in reader.get_pages_showing_field(
            reader.trailer["/Root"]["/AcroForm"]["/Fields"][-1]
        )
    ] == []
    assert [
        p.page_number
        for p in writer.get_pages_showing_field(
            writer._root_object["/AcroForm"]["/Fields"][-1]
        )
    ] == []


@pytest.mark.enable_socket
def test_extract_empty_page():
    """Cf #2533"""
    url = "https://github.com/py-pdf/pypdf/files/14718318/test.pdf"
    name = "iss2533.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name)))
    assert reader.pages[1].extract_text(extraction_mode="layout") == ""


@pytest.mark.enable_socket
def test_iss2815():
    """Cf #2815"""
    url = "https://github.com/user-attachments/files/16760725/crash-c1920c7a064649e1191d7879952ec252473fc7e6.pdf"
    name = "iss2815.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name)))
    assert reader.pages[0].extract_text() == "test command with wrong number of args"
