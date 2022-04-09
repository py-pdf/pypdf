# Adding a Watermark to a PDF

```python
from PyPDF2 import PdfFileWriter, PdfFileReader


# Read the watermark
watermark = PdfFileReader(open("watermark.pdf", "rb"))

# Read the page without watermark
reader = PdfFileReader(open("example.pdf", "rb"))
page = reader.pages[0]

# Add the watermark to the page
page.mergePage(watermark.pages[0])

# Add the page to the writer
writer = PdfFileWriter()
writer.addPage(page)

# finally, write the new document with a watermark
with open("PyPDF2-output.pdf", "wb") as fp:
    output.write(fp)
```
