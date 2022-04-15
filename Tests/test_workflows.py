# -*- coding: utf-8 -*-

import binascii
import os
import sys

import pytest

from PyPDF2 import PdfFileReader
from PyPDF2.constants import PageAttributes as PG

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")

sys.path.append(PROJECT_ROOT)


def test_PdfReaderFileLoad():
    """
    Test loading and parsing of a file. Extract text of the file and compare to expected
    textual output. Expected outcome: file loads, text matches expected.
    """

    with open(os.path.join(RESOURCE_ROOT, "crazyones.pdf"), "rb") as inputfile:
        # Load PDF file from file
        ipdf = PdfFileReader(inputfile)
        ipdf_p1 = ipdf.getPage(0)

        # Retrieve the text of the PDF
        with open(os.path.join(RESOURCE_ROOT, "crazyones.txt"), "rb") as pdftext_file:
            pdftext = pdftext_file.read()

        ipdf_p1_text = ipdf_p1.extractText().replace("\n", "").encode("utf-8")

        # Compare the text of the PDF to a known source
        assert ipdf_p1_text == pdftext, (
            "PDF extracted text differs from expected value.\n\nExpected:\n\n%r\n\nExtracted:\n\n%r\n\n"
            % (pdftext, ipdf_p1_text)
        )


def test_PdfReaderJpegImage():
    """
    Test loading and parsing of a file. Extract the image of the file and compare to expected
    textual output. Expected outcome: file loads, image matches expected.
    """

    with open(os.path.join(RESOURCE_ROOT, "jpeg.pdf"), "rb") as inputfile:
        # Load PDF file from file
        ipdf = PdfFileReader(inputfile)

        # Retrieve the text of the image
        with open(os.path.join(RESOURCE_ROOT, "jpeg.txt"), "r") as pdftext_file:
            imagetext = pdftext_file.read()

        ipdf_p0 = ipdf.getPage(0)
        xObject = ipdf_p0[PG.RESOURCES]["/XObject"].getObject()
        data = xObject["/Im4"].getData()

        # Compare the text of the PDF to a known source
        assert binascii.hexlify(data).decode() == imagetext, (
            "PDF extracted image differs from expected value.\n\nExpected:\n\n%r\n\nExtracted:\n\n%r\n\n"
            % (imagetext, binascii.hexlify(data).decode())
        )


def test_decrypt():
    with open(
        os.path.join(RESOURCE_ROOT, "libreoffice-writer-password.pdf"), "rb"
    ) as inputfile:
        ipdf = PdfFileReader(inputfile)
        assert ipdf.isEncrypted == True
        ipdf.decrypt("openpassword")
        assert ipdf.getNumPages() == 1
        assert ipdf.isEncrypted == True
        metadict = ipdf.getDocumentInfo()
        assert dict(metadict) == {
            "/CreationDate": "D:20220403203552+02'00'",
            "/Creator": "Writer",
            "/Producer": "LibreOffice 6.4",
        }
        # Is extractText() broken for encrypted files?
        # assert ipdf.getPage(0).extractText().replace('\n', '') == "\n˘\n\u02c7\u02c6˙\n\n\n˘\u02c7\u02c6˙\n\n"


@pytest.mark.parametrize("degree", [0, 90, 180, 270, 360, -90])
def test_rotate(degree):
    with open(os.path.join(RESOURCE_ROOT, "crazyones.pdf"), "rb") as inputfile:
        ipdf = PdfFileReader(inputfile)
        page = ipdf.getPage(0)
        page.rotateCounterClockwise(degree)


def test_rotate_45():
    with open(os.path.join(RESOURCE_ROOT, "crazyones.pdf"), "rb") as inputfile:
        ipdf = PdfFileReader(inputfile)
        page = ipdf.getPage(0)
        with pytest.raises(AssertionError):
            page.rotateCounterClockwise(45)
