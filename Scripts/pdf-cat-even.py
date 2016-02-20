#!/usr/bin/env python

# adapted from:
# how to merge pdf files so that each file begins on an odd page number?
#
# http://unix.stackexchange.com/a/66455

import sys

from PyPDF2 import PdfFileWriter, PdfFileReader


alignment = 2           # to align on even pages


output = PdfFileWriter()
output_page_number = 0
for filename in sys.argv[1:]:
    inpdf = PdfFileReader(open(filename, 'rb'))

    pages = [inpdf.getPage(i) for i in range(0, inpdf.getNumPages())]
    for p in pages:
        output.addPage(p)
        output_page_number += 1

    # blank pages until next alignment boundary
    while output_page_number % alignment != 0:
        output.addBlankPage()
        output_page_number += 1

# speedbump:  on python2, sys.stdout is opened as text, NOT binary
# clean this up sometime...
output.write(sys.stdout)
