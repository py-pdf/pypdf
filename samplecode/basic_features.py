#!/usr/bin/env python
from __future__ import print_function
from os.path import dirname, join

from pypdf4.pdf import PdfFileWriter, PdfFileReader

SAMPLE_CODE_ROOT = dirname(__file__)
SAMPLE_PDF_ROOT = join(SAMPLE_CODE_ROOT, "pdfsamples")


output = PdfFileWriter()
input1 = PdfFileReader(
    open(join(SAMPLE_PDF_ROOT, "Seige_of_Vicksburg_Sample_OCR.pdf"), "rb")
)

# Print how many pages input1 has:
print("document1.pdf has %d pages." % input1.getNumPages())

# Add page 1 from input1 to output document, unchanged
output.addPage(input1.getPage(0))

# Add page 2 from input1, but rotated clockwise 90 degrees
output.addPage(input1.getPage(1).rotateClockwise(90))

# Add page 3 from input1, rotated the other way:
output.addPage(input1.getPage(2).rotateCounterClockwise(90))
# Alt.: output.addPage(input1.getPage(2).rotateClockwise(270))

# Add page 4 from input1, but first add a watermark from another PDF:
page4 = input1.getPage(3)
watermark = PdfFileReader(
    open(join(SAMPLE_PDF_ROOT, "AutoCad_Diagram.pdf"), "rb")
)
page4.mergePage(watermark.getPage(0))
output.addPage(page4)

# Add page 5 from input1, but crop it to half size:
page5 = input1.getPage(4)
page5.mediaBox.upperRight = (
    page5.mediaBox.getUpperRight_x() / 2,
    page5.mediaBox.getUpperRight_y() / 2
)
output.addPage(page5)

# Add some Javascript to launch the print window on opening this PDF.
# The password dialog may prevent the print dialog from being shown,
# Comment the encrypted lines, if that's the case, to try this out
output.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")

# Encrypt your new PDF and add a password
password = "secret"
output.encrypt(password)

# Finally, write "output" to document-output.pdf
outputStream = open("PyPDF4-output.pdf", "wb")
output.write(outputStream)
