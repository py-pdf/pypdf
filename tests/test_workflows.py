import binascii
import os
import sys
from io import BytesIO
from pathlib import Path

import pytest

from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PyPDF2.constants import ImageAttributes as IA
from PyPDF2.constants import PageAttributes as PG
from PyPDF2.constants import Ressources as RES
from PyPDF2.errors import PdfReadError, PdfReadWarning
from PyPDF2.filters import _xobj_to_image

from . import get_pdf_from_url

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "resources")

sys.path.append(PROJECT_ROOT)


def test_PdfReaderFileLoad():
    """
    Test loading and parsing of a file. Extract text of the file and compare to expected
    textual output. Expected outcome: file loads, text matches expected.
    """

    with open(os.path.join(RESOURCE_ROOT, "crazyones.pdf"), "rb") as inputfile:
        # Load PDF file from file
        reader = PdfReader(inputfile)
        page = reader.pages[0]

        # Retrieve the text of the PDF
        with open(os.path.join(RESOURCE_ROOT, "crazyones.txt"), "rb") as pdftext_file:
            pdftext = pdftext_file.read()

        text = page.extract_text(Tj_sep="", TJ_sep="").encode("utf-8")

        # Compare the text of the PDF to a known source
        for expected_line, actual_line in zip(text.split(b"\n"), pdftext.split(b"\n")):
            assert expected_line == actual_line

        assert text == pdftext, (
            "PDF extracted text differs from expected value.\n\nExpected:\n\n%r\n\nExtracted:\n\n%r\n\n"
            % (pdftext, text)
        )


def test_PdfReaderJpegImage():
    """
    Test loading and parsing of a file. Extract the image of the file and compare to expected
    textual output. Expected outcome: file loads, image matches expected.
    """

    with open(os.path.join(RESOURCE_ROOT, "jpeg.pdf"), "rb") as inputfile:
        # Load PDF file from file
        reader = PdfReader(inputfile)

        # Retrieve the text of the image
        with open(os.path.join(RESOURCE_ROOT, "jpeg.txt")) as pdftext_file:
            imagetext = pdftext_file.read()

        page = reader.pages[0]
        x_object = page[PG.RESOURCES]["/XObject"].get_object()
        data = x_object["/Im4"].get_data()

        # Compare the text of the PDF to a known source
        assert binascii.hexlify(data).decode() == imagetext, (
            "PDF extracted image differs from expected value.\n\nExpected:\n\n%r\n\nExtracted:\n\n%r\n\n"
            % (imagetext, binascii.hexlify(data).decode())
        )


def test_decrypt():
    with open(
        os.path.join(RESOURCE_ROOT, "libreoffice-writer-password.pdf"), "rb"
    ) as inputfile:
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
    inputfile = os.path.join(RESOURCE_ROOT, "libreoffice-writer-password.pdf")
    reader = PdfReader(inputfile)
    assert reader.is_encrypted is True
    reader.decrypt("openpassword")
    assert (
        reader.pages[0]
        .extract_text()
        .replace("\n", "")
        .strip()
        .startswith("Lorem ipsum dolor sit amet")
    )


@pytest.mark.parametrize("degree", [0, 90, 180, 270, 360, -90])
def test_rotate(degree):
    with open(os.path.join(RESOURCE_ROOT, "crazyones.pdf"), "rb") as inputfile:
        reader = PdfReader(inputfile)
        page = reader.pages[0]
        page.rotate(degree)


def test_rotate_45():
    with open(os.path.join(RESOURCE_ROOT, "crazyones.pdf"), "rb") as inputfile:
        reader = PdfReader(inputfile)
        page = reader.pages[0]
        with pytest.raises(ValueError) as exc:
            page.rotate(45)
        assert exc.value.args[0] == "Rotation angle must be a multiple of 90"


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
        # 6 instead of 5: as there is an issue in page 5 (missing objects)
        # and too complex to handle the warning without hiding real regressions
        (True, "https://arxiv.org/pdf/1601.03642.pdf", [0, 1, 5, 7]),
        (
            True,
            "https://github.com/py-pdf/PyPDF2/files/3796761/17343_2008_Order_09-Jan-2019.pdf",
            [0, 1],
        ),
        (
            True,
            "https://github.com/py-pdf/PyPDF2/files/8884471/ssi_manwaring.pdf",
            [0, 1],
        ),
        (True, "https://github.com/py-pdf/PyPDF2/files/8884469/999092.pdf", [0, 1]),
        (
            True,
            "file://" + os.path.join(RESOURCE_ROOT, "test Orient.pdf"),
            [0],
        ),  # TODO: preparation of text orientation validation
        (
            True,
            "https://github.com/py-pdf/PyPDF2/files/8884470/fdocuments.in_sweet-fundamentals-of-crystallography.pdf",
            [0, 1, 34, 35, 36, 118, 119, 120, 121],
        ),
        (True, "https://github.com/py-pdf/PyPDF2/files/8884493/998167.pdf", [0]),
        (
            True,
            "https://corpora.tika.apache.org/base/docs/govdocs1/971/971703.pdf",
            [0, 1, 5, 8, 14],
        ),
        (  # faulty PDF, wrongly linearized and with 2 trailer, second with /Root
            True,
            "https://corpora.tika.apache.org/base/docs/govdocs1/989/989691.pdf",
            [0],
        ),
    ],
)
def test_extract_textbench(enable, url, pages, print_result=False):
    if not enable:
        return
    try:
        reader = PdfReader(BytesIO(get_pdf_from_url(url, url.split("/")[-1])))
        for page_number in pages:
            if print_result:
                print(f"**************** {url} / page {page_number} ****************")
            rst = reader.pages[page_number].extract_text()
            if print_result:
                print(f"{rst}\n*****************************\n")
    except PdfReadWarning:
        pass


@pytest.mark.parametrize(
    ("base_path", "overlay_path"),
    [
        (
            "resources/crazyones.pdf",
            "sample-files/013-reportlab-overlay/reportlab-overlay.pdf",
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/935/935981.pdf",
            "sample-files/013-reportlab-overlay/reportlab-overlay.pdf",
        ),
    ],
)
def test_overlay(base_path, overlay_path):
    if base_path.startswith("http"):
        base_path = BytesIO(get_pdf_from_url(base_path, name="tika-935981.pdf"))
    else:
        base_path = os.path.join(PROJECT_ROOT, base_path)
    reader = PdfReader(base_path)
    writer = PdfWriter()

    reader_overlay = PdfReader(os.path.join(PROJECT_ROOT, overlay_path))
    overlay = reader_overlay.pages[0]

    for page in reader.pages:
        page.merge_page(overlay)
        writer.add_page(page)
    with open("dont_commit_overlay.pdf", "wb") as fp:
        writer.write(fp)

    # Cleanup
    os.remove("dont_commit_overlay.pdf")


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/924/924546.pdf",
            "tika-924546.pdf",
        )
    ],
)
def test_merge_with_warning(url, name):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)
    merger = PdfMerger()
    merger.append(reader)
    # This could actually be a performance bottleneck:
    with pytest.warns(
        PdfReadWarning, match="^Unable to resolve .*, returning NullObject instead"
    ):
        merger.write("tmp.merged.pdf")

    # Cleanup
    os.remove("tmp.merged.pdf")


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/980/980613.pdf",
            "tika-980613.pdf",
        )
    ],
)
def test_merge(url, name):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)
    merger = PdfMerger()
    merger.append(reader)
    merger.write("tmp.merged.pdf")

    # Cleanup
    os.remove("tmp.merged.pdf")


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/935/935996.pdf",
            "tika-935996.pdf",
        )
    ],
)
def test_get_metadata(url, name):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)
    reader.metadata


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/938/938702.pdf",
            "tika-938702.pdf",
        )
    ],
)
def test_extract_text(url, name):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)
    reader.metadata


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/938/938702.pdf",
            "tika-938702.pdf",
        )
    ],
)
def test_compress(url, name):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)
    # TODO: which page exactly?
    # TODO: Is it reasonable to have an exception here?
    with pytest.raises(PdfReadError) as exc:
        for page in reader.pages:
            page.compress_content_streams()
    assert exc.value.args[0] == "Unexpected end of stream"


def test_get_fields():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/961/961883.pdf"
    name = "tika-961883.pdf"
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)
    with open("tmp.txt", "w") as fp:
        with pytest.warns(PdfReadWarning, match="Object 2 0 not defined."):
            retrieved_fields = reader.get_fields(fileobj=fp)

    assert retrieved_fields == {}

    # Cleanup
    os.remove("tmp.txt")


def test_scale_rectangle_indirect_object():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/999/999944.pdf"
    name = "tika-999944.pdf"
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)

    for page in reader.pages:
        page.scale(sx=2, sy=3)


def test_merge_output():
    # Arrange
    base = os.path.join(RESOURCE_ROOT, "Seige_of_Vicksburg_Sample_OCR.pdf")
    crazy = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    expected = os.path.join(
        RESOURCE_ROOT, "Seige_of_Vicksburg_Sample_OCR-crazyones-merged.pdf"
    )

    # Act
    merger = PdfMerger(strict=True)
    with pytest.warns(PdfReadWarning):
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
        assert (
            False
        ), f"len(actual) = {len(actual):,} vs len(expected) = {len(expected_data):,}"

    # Cleanup
    merger.close()


def test_image_extraction():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/994/994636.pdf"
    name = "tika-994636.pdf"
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)

    images_extracted = []
    root = Path("extracted-images")
    if not root.exists():
        os.mkdir(root)

    for page in reader.pages:
        if RES.XOBJECT in page[PG.RESOURCES]:
            x_object = page[PG.RESOURCES][RES.XOBJECT].get_object()

            for obj in x_object:
                if x_object[obj][IA.SUBTYPE] == "/Image":
                    extension, byte_stream = _xobj_to_image(x_object[obj])
                    if extension is not None:
                        filename = root / (obj[1:] + extension)
                        with open(filename, "wb") as img:
                            img.write(byte_stream)
                        images_extracted.append(filename)

    # Cleanup
    do_cleanup = True  # set this to False for manual inspection
    if do_cleanup:
        for filepath in images_extracted:
            if os.path.exists(filepath):
                os.remove(filepath)
