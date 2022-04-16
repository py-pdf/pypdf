import os

import pytest

from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.errors import PdfReadError
from PyPDF2.pdf import convertToInt

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


def test_basic_features():
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    reader = PdfFileReader(pdf_path)
    writer = PdfFileWriter()

    # print how many pages input1 has:
    print("document1.pdf has %d pages." % reader.getNumPages())

    # add page 1 from input1 to output document, unchanged
    writer.addPage(reader.getPage(0))

    # add page 2 from input1, but rotated clockwise 90 degrees
    writer.addPage(reader.getPage(0).rotateClockwise(90))

    # add page 3 from input1, rotated the other way:
    writer.addPage(reader.getPage(0).rotateCounterClockwise(90))
    # alt: output.addPage(input1.getPage(0).rotateClockwise(270))

    # add page 4 from input1, but first add a watermark from another PDF:
    page4 = reader.getPage(0)
    watermark_pdf = pdf_path
    watermark = PdfFileReader(watermark_pdf)
    page4.mergePage(watermark.getPage(0))
    writer.addPage(page4)

    # add page 5 from input1, but crop it to half size:
    page5 = reader.getPage(0)
    page5.mediaBox.upperRight = (
        page5.mediaBox.getUpperRight_x() / 2,
        page5.mediaBox.getUpperRight_y() / 2,
    )
    writer.addPage(page5)

    # add some Javascript to launch the print window on opening this PDF.
    # the password dialog may prevent the print dialog from being shown,
    # comment the the encription lines, if that's the case, to try this out
    writer.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")

    # encrypt your new PDF and add a password
    password = "secret"
    writer.encrypt(password)

    # finally, write "output" to PyPDF2-output.pdf
    tmp_path = "PyPDF2-output.pdf"
    with open(tmp_path, "wb") as output_stream:
        writer.write(output_stream)

    # cleanup
    os.remove(tmp_path)


def test_convertToInt():
    with pytest.raises(PdfReadError) as exc:
        convertToInt(256, 16)
    assert exc.value.args[0] == "invalid size in convertToInt"
