import os

import pytest

from PyPDF2 import PdfReader, PdfWriter

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "resources")


def test_basic_features():
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    assert len(reader.pages) == 1

    # add page 1 from input1 to output document, unchanged
    writer.add_page(reader.pages[0])

    # add page 2 from input1, but rotated clockwise 90 degrees
    writer.add_page(reader.pages[0].rotate_clockwise(90))

    # add page 3 from input1, rotated the other way:
    writer.add_page(reader.pages[0].rotateCounterClockwise(90))
    # alt: output.addPage(input1.pages[0].rotate_clockwise(270))

    # add page 4 from input1, but first add a watermark from another PDF:
    page4 = reader.pages[0]
    watermark_pdf = pdf_path
    watermark = PdfReader(watermark_pdf)
    page4.merge_page(watermark.pages[0])
    writer.add_page(page4)

    # add page 5 from input1, but crop it to half size:
    page5 = reader.pages[0]
    page5.mediabox.upper_right = (
        page5.mediabox.right / 2,
        page5.mediabox.top / 2,
    )
    writer.add_page(page5)

    # add some Javascript to launch the print window on opening this PDF.
    # the password dialog may prevent the print dialog from being shown,
    # comment the the encription lines, if that's the case, to try this out
    writer.add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")

    # encrypt your new PDF and add a password
    password = "secret"
    writer.encrypt(password)

    # finally, write "output" to PyPDF2-output.pdf
    tmp_path = "PyPDF2-output.pdf"
    with open(tmp_path, "wb") as output_stream:
        writer.write(output_stream)

    # cleanup
    os.remove(tmp_path)
