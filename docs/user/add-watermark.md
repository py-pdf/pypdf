# Adding a Watermark to a PDF

```python
from PyPDF2 import PdfWriter, PdfReader


# Read the watermark
watermark = PdfReader("watermark.pdf")

# Read the page without watermark
reader = PdfReader("example.pdf")
page = reader.pages[0]

# Add the watermark to the page
page.merge_page(watermark.pages[0])

# Add the page to the writer
writer = PdfWriter()
writer.add_page(page)

# finally, write the new document with a watermark
with open("PyPDF2-output.pdf", "wb") as fp:
    output.write(fp)
```
