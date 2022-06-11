# Reduce PDF Size

There are multiple ways to reduce the size of a given PDF file. The easiest
one is to remove content (e.g. images) or pages.

## Remove images


```python
import PyPDF2

reader = PyPDF2.PdfReader("example.pdf")
writer = PyPDF2.PdfWriter()

for page in reader.pages:
    writer.add_page(page)

writer.remove_images()

with open("out.pdf", "wb") as f:
    writer.write(f)
```

## Compression

```python
import PyPDF2

reader = PyPDF2.PdfReader("example.pdf")
writer = PyPDF2.PdfWriter()

for page in reader.pages:
    page.compress_content_streams()
    writer.add_page(page)

with open("out.pdf", "wb") as f:
    writer.write(f)
```
