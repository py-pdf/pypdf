# Reduce PDF Size

There are multiple ways to reduce the size of a given PDF file. The easiest
one is to remove content (e.g. images) or pages.

## Remove images


```python
import PyPDF2

reader = PyPDF2.PdfFileReader("example.pdf")
writer = PyPDF2.PdfFileWriter()

for page in reader.pages:
    writer.addPage(page)

writer.removeImages()

with open("out.pdf", "wb") as f:
    writer.write(f)
```

## Compression

```python
import PyPDF2

reader = PyPDF2.PdfFileReader("example.pdf")
writer = PyPDF2.PdfFileWriter()

for page in reader.pages:
    page.compressContentStreams()
    writer.addPage(page)

with open("out.pdf", "wb") as f:
    writer.write(f)
```
