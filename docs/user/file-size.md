# Reduce PDF Size

There are multiple ways to reduce the size of a given PDF file. The easiest
one is to remove content (e.g. images) or pages.

## Removing duplication

Some PDF documents contain the same object multiple times. For example, if an
image appears three times in a PDF it could be embedded three times. Or it can
be embedded once and referenced twice.

This can be done by reading and writing the file:

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("big-old-file.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

writer.add_metadata(reader.metadata)

with open("smaller-new-file.pdf", "wb") as fp:
    writer.write(fp)
```

It depends on the PDF how well this works, but we have seen an 86% file
reduction (from 5.7 MB to 0.8 MB) within a real PDF.


## Removing Images


```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("example.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

writer.remove_images()

with open("out.pdf", "wb") as f:
    writer.write(f)
```

## Lossless Compression

pypdf supports the FlateDecode filter which uses the zlib/deflate compression
method. It is a lossless compression, meaning the resulting PDF looks exactly
the same.

Deflate compression can be applied to a page via [`page.compress_content_streams`](https://pypdf.readthedocs.io/en/latest/modules/PageObject.html#pypdf._page.PageObject.compress_content_streams):

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("example.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

for page in writer.pages:
    # ⚠️ This has to be done on the writer, not the reader!
    page.compress_content_streams()  # This is CPU intensive!

with open("out.pdf", "wb") as f:
    writer.write(f)
```

Using this method, we have seen a reduction by 70% (from 11.8 MB to 3.5 MB)
with a real PDF.

## Removing Sources

When a page is removed from page list, the source will remain in the PDF file. The data may be still be used somewhere else.

Hence just removing a page from the page list will reduce the page count, but not the file size. 
To not include the code, the pages should not be added using `PdfWriter.append()` selecting the good pages only
- Issues can arise with poor PDF formatting such as when all pages are linked to the same resource, making dropping references useless since there is one source for all pages.
- Cropping is an ineffective way of reducing the file size, as the external part of the source image will still be present. Just the viewboxes are adjusted.
