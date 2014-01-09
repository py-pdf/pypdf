#!/usr/bin/env python
"Make some simple multipage pdf files."

from reportlab.pdfgen import canvas
from sys import argv

point = 1
inch = 72

TEXT = """%s    page %d of %d

a wonderful file
created with Sample_Code/makepages.py"""

def make_pdf_file(output_filename, np):
    title = output_filename
    c = canvas.Canvas(output_filename, pagesize=(8.5 * inch, 11 * inch))
    c.setStrokeColorRGB(0,0,0)
    c.setFillColorRGB(0,0,0)
    c.setFont("Helvetica", 12 * point) 
    for pn in range(1, np + 1):
        v = 10 * inch
        for subtline in (TEXT % (output_filename, pn, np)).split( '\n' ):
            c.drawString( 1 * inch, v, subtline )
            v -= 12 * point
        c.showPage()
    c.save()
    
if __name__ == "__main__":
    nps = [None, 5, 11, 17]
    for i, np in enumerate(nps):
        if np:
            filename = "simplest_%d.pdf" % i
            make_pdf_file(filename, np)
            print "Wrote", filename
