Example:

    from pyPdf import PdfFileWriter, PdfFileReader

    output = PdfFileWriter()
    input1 = PdfFileReader(file("document1.pdf", "rb"))

    # add page 1 from input1 to output document, unchanged
    output.addPage(input1.getPage(0))

    # add page 2 from input1, but rotated clockwise 90 degrees
    output.addPage(input1.getPage(1).rotateClockwise(90))

    # add page 3 from input1, rotated the other way:
    output.addPage(input1.getPage(2).rotateCounterClockwise(90))
    # alt: output.addPage(input1.getPage(2).rotateClockwise(270))

    # add page 4 from input1, but first add a watermark from another pdf:
    page4 = input1.getPage(3)
    watermark = PdfFileReader(file("watermark.pdf", "rb"))
    page4.mergePage(watermark.getPage(0))

    # add page 5 from input1, but crop it to half size:
    page5 = input1.getPage(4)
    page5.mediaBox.upperRight = (
        page5.mediaBox.getUpperRight_x() / 2,
        page5.mediaBox.getUpperRight_y() / 2
    )
    output.addPage(page5)

    # print how many pages input1 has:
    print "document1.pdf has %s pages." % input1.getNumPages())

    # finally, write "output" to document-output.pdf
    outputStream = file("document-output.pdf", "wb")
    output.write(outputStream)


