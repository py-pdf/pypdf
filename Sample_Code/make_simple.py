#!/usr/bin/env python
"""Sample code to make a few simple pdf files of various page counts."""

from __future__ import print_function
from sys import argv

from reportlab.pdfgen import canvas

POINT = 1
INCH = 72

TEXT = """%s    page %d of %d

a wonderful file
created with Sample_Code/makesimple.py"""


def make_pdf_file(output_filename, page_count):
    title = output_filename
    c = canvas.Canvas(output_filename, pagesize=(8.5 * INCH, 11 * INCH))
    c.setStrokeColorRGB(0,0,0)
    c.setFillColorRGB(0,0,0)
    c.setFont("Helvetica", 12 * POINT)
    for page_no in range(1, page_count + 1):
        # The x-axis is at the bottom of the page, so 10 * INCH is 1 inch from the top.
        vertical_pos = 10 * INCH
        left_margin = 1 * INCH
        for text_line in (TEXT % (output_filename, page_no, page_count)).split( '\n' ):
            c.drawString(left_margin, vertical_pos, text_line)
            vertical_pos -= 12 * POINT
        c.showPage()
    c.save()

if __name__ == "__main__":
    target_page_counts = [None, 5, 11, 17]
    for i, target_page_count in enumerate(target_page_counts):
        if target_page_count:
            filename = "simple%d.pdf" % i
            make_pdf_file(filename, target_page_count)
            print ("Wrote", filename)
