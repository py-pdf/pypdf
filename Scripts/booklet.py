#!/usr/bin/env python

"""
Layout the pages from a PDF file to print a booklet or brochure.

The resulting media size is twice the size of the first page
of the source document. If you print the resulting PDF in duplex
(short edge), you get a center fold brochure that you can staple
together and read as a booklet.
"""

from __future__ import division, print_function

import argparse

import PyPDF2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=argparse.FileType("rb"))
    parser.add_argument("output")
    args = parser.parse_args()

    reader = PyPDF2.PdfFileReader(args.input)
    numPages = reader.getNumPages()
    print("Pages in file:", numPages)

    pagesPerSheet = 4
    virtualPages = (numPages + pagesPerSheet - 1) // pagesPerSheet * pagesPerSheet

    firstPage = reader.getPage(0)
    mb = firstPage.mediaBox
    pageWidth = 2 * mb.getWidth()
    pageHeight = mb.getHeight()
    print("Medium size:", "{}x{}".format(pageWidth, pageHeight))

    writer = PyPDF2.PdfFileWriter()

    def scale(page):
        return min(
            mb.getWidth() / page.mediaBox.getWidth(),
            mb.getHeight() / page.mediaBox.getHeight(),
        )

    def mergePage(dst, src, xOffset):
        pageScale = scale(src)
        print("scaling by", pageScale)
        dx = (mb.getWidth() - pageScale * src.mediaBox.getWidth()) / 2
        dy = (mb.getHeight() - pageScale * src.mediaBox.getHeight()) / 2
        dst.mergeScaledTranslatedPage(src, scale(src), xOffset + dx, dy)

    def mergePageByNumber(dstPage, pageNumber, xOffset):
        if pageNumber >= numPages:
            return
        print("merging page", pageNumber, "with offset", xOffset)
        page = reader.getPage(pageNumber)
        mergePage(dstPage, page, xOffset)

    for i in range(virtualPages // 2):
        page = writer.addBlankPage(width=pageWidth, height=pageHeight)
        offsets = [0, pageWidth // 2]
        if i % 2 == 0:
            offsets.reverse()
        mergePageByNumber(page, i, offsets[0])
        mergePageByNumber(page, virtualPages - i - 1, offsets[1])

    with open(args.output, "wb") as fp:
        writer.write(fp)


if __name__ == "__main__":
    main()
