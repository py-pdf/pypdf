# Cropping and Transforming PDFs

```python
from PyPDF2 import PdfFileWriter, PdfFileReader

reader = PdfFileReader("example.pdf")
writer = PdfFileWriter()

# add page 1 from reader to output document, unchanged:
writer.addPage(reader.pages[0])

# add page 2 from reader, but rotated clockwise 90 degrees:
writer.addPage(reader.pages[1].rotateClockwise(90))

# add page 3 from reader, but crop it to half size:
page3 = reader.pages[2]
page3.mediaBox.upperRight = (
    page3.mediaBox.getUpperRight_x() / 2,
    page3.mediaBox.getUpperRight_y() / 2,
)
writer.addPage(page3)

# add some Javascript to launch the print window on opening this PDF.
# the password dialog may prevent the print dialog from being shown,
# comment the the encription lines, if that's the case, to try this out:
writer.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")

# write to document-output.pdf
with open("PyPDF2-output.pdf", "wb") as fp:
    writer.write(fp)
```
