"""
Tests in this module behave like user code.

They don't mock/patch anything, they cover typical user needs.
"""

import binascii
import os
import sys
from io import BytesIO
from pathlib import Path
from re import findall

import pytest

from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PyPDF2.constants import ImageAttributes as IA
from PyPDF2.constants import PageAttributes as PG
from PyPDF2.constants import Ressources as RES
from PyPDF2.errors import PdfReadError, PdfReadWarning
from PyPDF2.filters import _xobj_to_image

from . import get_pdf_from_url, normalize_warnings

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"

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
    # comment the the encription lines, if that's the case, to try this out
    writer.add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")

    # encrypt your new PDF and add a password
    password = "secret"
    writer.encrypt(password)

    # finally, write "output" to PyPDF2-output.pdf
    write_path = tmp_path / "PyPDF2-output.pdf"
    with open(write_path, "wb") as output_stream:
        writer.write(output_stream)


def test_dropdown_items():
    inputfile = RESOURCE_ROOT / "libreoffice-form.pdf"
    reader = PdfReader(inputfile)
    fields = reader.get_fields()
    assert "/Opt" in fields["Nationality"].keys()


def test_PdfReaderFileLoad():
    """
    Test loading and parsing of a file. Extract text of the file and compare to expected
    textual output. Expected outcome: file loads, text matches expected.
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
        assert binascii.hexlify(data).decode() == imagetext, (
            "PDF extracted image differs from expected value.\n\nExpected:\n\n%r\n\nExtracted:\n\n%r\n\n"
            % (imagetext, binascii.hexlify(data).decode())
        )


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
        .replace("\n", "")
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
        (True, "https://github.com/py-pdf/PyPDF2/files/9174594/2017.pdf", [0]),
        # #1145, remaining issue (empty arguments for FlateEncoding)
        (
            True,
            "https://github.com/py-pdf/PyPDF2/files/9175966/2015._pb_decode_pg0.pdf",
            [0],
        ),
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
            "file://" + str(RESOURCE_ROOT / "test Orient.pdf"),
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


def test_orientations():
    p = PdfReader(RESOURCE_ROOT / "test Orient.pdf").pages[0]
    try:
        p.extract_text("", "")
    except DeprecationWarning:
        pass
    else:
        raise Exception("DeprecationWarning expected")
    try:
        p.extract_text("", "", 0)
    except DeprecationWarning:
        pass
    else:
        raise Exception("DeprecationWarning expected")
    try:
        p.extract_text("", "", 0, 200)
    except DeprecationWarning:
        pass
    else:
        raise Exception("DeprecationWarning expected")

    try:
        p.extract_text(Tj_sep="", TJ_sep="")
    except DeprecationWarning:
        pass
    else:
        raise Exception("DeprecationWarning expected")
    assert findall("\\((.)\\)", p.extract_text()) == ["T", "B", "L", "R"]
    try:
        p.extract_text(None)
    except Exception:
        pass
    else:
        raise Exception("Argument 1 check invalid")
    try:
        p.extract_text("", 0)
    except Exception:
        pass
    else:
        raise Exception("Argument 2 check invalid")
    try:
        p.extract_text("", "", None)
    except Exception:
        pass
    else:
        raise Exception("Argument 3 check invalid")
    try:
        p.extract_text("", "", 0, "")
    except Exception:
        pass
    else:
        raise Exception("Argument 4 check invalid")
    try:
        p.extract_text(0, "")
    except Exception:
        pass
    else:
        raise Exception("Argument 1 new syntax check invalid")

    p.extract_text(0, 0)
    p.extract_text(orientations=0)

    for (req, rst) in (
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
        base_path = PROJECT_ROOT / base_path
    reader = PdfReader(base_path)
    writer = PdfWriter()

    reader_overlay = PdfReader(PROJECT_ROOT / overlay_path)
    overlay = reader_overlay.pages[0]

    for page in reader.pages:
        page.merge_page(overlay)
        writer.add_page(page)
    with open("dont_commit_overlay.pdf", "wb") as fp:
        writer.write(fp)

    # Cleanup
    os.remove("dont_commit_overlay.pdf")  # remove for manual inspection


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/924/924546.pdf",
            "tika-924546.pdf",
        )
    ],
)
def test_merge_with_warning(tmp_path, url, name):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)
    merger = PdfMerger()
    merger.append(reader)
    # This could actually be a performance bottleneck:
    merger.write(tmp_path / "tmp.merged.pdf")


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/980/980613.pdf",
            "tika-980613.pdf",
        )
    ],
)
def test_merge(tmp_path, url, name):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)
    merger = PdfMerger()
    merger.append(reader)
    merger.write(tmp_path / "tmp.merged.pdf")


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
    ("url", "name", "strict", "exception"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/938/938702.pdf",
            "tika-938702.pdf",
            False,
            (PdfReadError, "Unexpected end of stream"),
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/942/942358.pdf",
            "tika-942358.pdf",
            False,
            None,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/911/911260.pdf",
            "tika-911260.pdf",
            False,
            None,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/992/992472.pdf",
            "tika-992472.pdf",
            False,
            None,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/978/978477.pdf",
            "tika-978477.pdf",
            False,
            None,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/960/960317.pdf",
            "tika-960317.pdf",
            False,
            None,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/930/930513.pdf",
            "tika-930513.pdf",
            False,
            None,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/918/918113.pdf",
            "tika-918113.pdf",
            True,
            None,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/940/940704.pdf",
            "tika-940704.pdf",
            True,
            None,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/976/976488.pdf",
            "tika-976488.pdf",
            True,
            None,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/948/948176.pdf",
            "tika-948176.pdf",
            True,
            None,
        ),
    ],
)
def test_extract_text(url, name, strict, exception):
    data = BytesIO(get_pdf_from_url(url, name=name))
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


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/938/938702.pdf",
            "tika-938702.pdf",
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/957/957304.pdf",
            "tika-938702.pdf",
        ),
    ],
)
def test_compress_raised(url, name):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)
    # TODO: which page exactly?
    # TODO: Is it reasonable to have an exception here?
    with pytest.raises(PdfReadError) as exc:
        for page in reader.pages:
            page.compress_content_streams()
    assert exc.value.args[0] == "Unexpected end of stream"


@pytest.mark.parametrize(
    ("url", "name", "strict"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/915/915194.pdf",
            "tika-915194.pdf",
            False,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/950/950337.pdf",
            "tika-950337.pdf",
            False,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/962/962292.pdf",
            "tika-962292.pdf",
            True,
        ),
    ],
)
def test_compress(url, name, strict):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data, strict=strict)
    # TODO: which page exactly?
    # TODO: Is it reasonable to have an exception here?
    for page in reader.pages:
        page.compress_content_streams()


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/961/961883.pdf",
            "tika-961883.pdf",
        ),
    ],
)
def test_get_fields_warns(tmp_path, caplog, url, name):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)
    write_path = tmp_path / "tmp.txt"
    with open(write_path, "w") as fp:
        retrieved_fields = reader.get_fields(fileobj=fp)

    assert retrieved_fields == {}
    assert normalize_warnings(caplog.text) == ["Object 2 0 not defined."]


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/942/942050.pdf",
            "tika-942050.pdf",
        ),
    ],
)
def test_get_fields_no_warning(tmp_path, url, name):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)
    write_path = tmp_path / "tmp.txt"
    with open(write_path, "w") as fp:
        retrieved_fields = reader.get_fields(fileobj=fp)

    assert len(retrieved_fields) == 10


def test_scale_rectangle_indirect_object():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/999/999944.pdf"
    name = "tika-999944.pdf"
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)

    for page in reader.pages:
        page.scale(sx=2, sy=3)


def test_merge_output(caplog):
    # Arrange
    base = RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf"
    crazy = RESOURCE_ROOT / "crazyones.pdf"
    expected = RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR-crazyones-merged.pdf"

    # Act
    merger = PdfMerger(strict=True)
    merger.append(base)
    msg = "Xref table not zero-indexed. ID numbers for objects will be corrected."
    assert normalize_warnings(caplog.text) == [msg]
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


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/994/994636.pdf",
            "tika-994636.pdf",
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/952/952133.pdf",
            "tika-952133.pdf",
        ),
        (  # JPXDecode
            "https://corpora.tika.apache.org/base/docs/govdocs1/914/914568.pdf",
            "tika-914568.pdf",
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/952/952016.pdf",
            "tika-952016.pdf",
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/965/965118.pdf",
            "tika-952016.pdf",
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/959/959184.pdf",
            "tika-959184.pdf",
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/958/958496.pdf",
            "tika-958496.pdf",
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/972/972174.pdf",
            "tika-972174.pdf",
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/972/972243.pdf",
            "tika-972243.pdf",
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/969/969502.pdf",
            "tika-969502.pdf",
        ),
    ],
)
def test_image_extraction(url, name):
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


def test_image_extraction_strict():
    # Emits log messages
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/914/914102.pdf"
    name = "tika-914102.pdf"
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data, strict=True)

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


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/977/977609.pdf",
            "tika-977609.pdf",
        ),
    ],
)
def test_image_extraction2(url, name):
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


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/918/918137.pdf",
            "tika-918137.pdf",
        ),
        (
            "https://unglueit-files.s3.amazonaws.com/ebf/7552c42e9280b4476e59e77acc0bc812.pdf",
            "7552c42e9280b4476e59e77acc0bc812.pdf",
        ),
    ],
)
def test_get_outline(url, name):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)
    reader.outline


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/935/935981.pdf",
            "tika-935981.pdf",
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/937/937334.pdf",
            "tika-937334.pdf",
        ),
    ],
)
def test_get_xfa(url, name):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data)
    reader.xfa


@pytest.mark.parametrize(
    ("url", "name", "strict"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/988/988698.pdf",
            "tika-988698.pdf",
            False,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/914/914133.pdf",
            "tika-988698.pdf",
            False,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/912/912552.pdf",
            "tika-912552.pdf",
            False,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/914/914102.pdf",
            "tika-914102.pdf",
            True,
        ),
    ],
)
def test_get_fonts(url, name, strict):
    data = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(data, strict=strict)
    for page in reader.pages:
        page._get_fonts()


@pytest.mark.parametrize(
    ("url", "name", "strict"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/942/942303.pdf",
            "tika-942303.pdf",
            True,
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/935/935981.pdf",
            "tika-935981.pdf",
            True,
        ),
    ],
)
def test_get_xmp(url, name, strict):
    data = BytesIO(get_pdf_from_url(url, name=name))
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
