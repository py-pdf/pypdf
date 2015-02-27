from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.pdf import PageObject

merged = PdfFileWriter()
a4 = PageObject.createBlankPage(width=595, height=842)

p0 = PdfFileReader('0.pdf')
a4.mergePage(p0.getPage(0))

p1 = PdfFileReader('1.pdf')
a4.mergePage(p1.getPage(0))

merged.addPage(a4)
with open('merge.pdf', 'wb') as f:
    merged.write(f)
