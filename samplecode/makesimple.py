#!/usr/bin/env python
"""
Make some simple multi-page PDF files.
"""

from __future__ import print_function

from reportlab.pdfgen import canvas

point = 1
inch = 72

TEXT = """%s    page %d of %d

a wonderful file
created with samplecode/makesimple.py"""


def makePdfFile(output_filename, np):
    _title = output_filename
    c = canvas.Canvas(output_filename, pagesize=(8.5 * inch, 11 * inch))
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 12 * point)

    for pn in range(1, np + 1):
        v = 10 * inch

        for subtline in (TEXT % (output_filename, pn, np)).split('\n'):
            c.drawString(1 * inch, v, subtline)
            v -= 12 * point

        c.showPage()
    c.save()


if __name__ == "__main__":
    NPS = [None, 5, 11, 17]

    for i, NP in enumerate(NPS):
        if NP:
            filename = "simple%d.pdf" % i
            makePdfFile(filename, NP)
            print("Wrote", filename)
