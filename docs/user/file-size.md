# Reduce PDF File Size

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

if reader.metadata is not None:
    writer.add_metadata(reader.metadata)

with open("smaller-new-file.pdf", "wb") as fp:
    writer.write(fp)
```

It depends on the PDF how well this works, but we have seen an 86% file
reduction (from 5.7 MB to 0.8 MB) within a real PDF.


## Removing Images


```python
from pypdf import PdfWriter

writer = PdfWriter(clone_from="example.pdf")

writer.remove_images()

with open("out.pdf", "wb") as f:
    writer.write(f)
```

## Reducing Image Quality

If we reduce the quality of the images within the PDF, we can **sometimes**
reduce the file size of the PDF overall. That depends on how well the reduced
quality image can be compressed.

```python
from pypdf import PdfWriter

writer = PdfWriter(clone_from="example.pdf")

for page in writer.pages:
    for img in page.images:
        img.replace(img.image, quality=80)

with open("out.pdf", "wb") as f:
    writer.write(f)
```

## Lossless Compression

pypdf supports the FlateDecode filter which uses the zlib/deflate compression
method. It is a lossless compression, meaning the resulting PDF looks exactly
the same.

Deflate compression can be applied to a page via
[`page.compress_content_streams`](https://pypdf.readthedocs.io/en/latest/modules/PageObject.html#pypdf._page.PageObject.compress_content_streams):

```python
from pypdf import PdfWriter

writer = PdfWriter(clone_from="example.pdf")

for page in writer.pages:
    page.compress_content_streams()  # This is CPU intensive!

with open("out.pdf", "wb") as f:
    writer.write(f)
```

`page.compress_content_streams` uses [`zlib.compress`](https://docs.python.org/3/library/zlib.html#zlib.compress)
and supports the `level` parameter: `level=0` means no compression,
`level=9` refers to the highest compression.

Using this method, we have seen a reduction by 70% (from 11.8 MB to 3.5 MB)
with a real PDF.

## Removing Sources

When a page is removed from the page list, its content will still be present in
the PDF file. This means that the data may still be used elsewhere.

Simply removing a page from the page list will reduce the page count but not the
file size. In order to exclude the content completely, the pages should not be
added to the PDF using the PdfWriter.append() function. Instead, only the
desired pages should be selected for inclusion
(note: [PR #1843](https://github.com/py-pdf/pypdf/pull/1843) will add a page
deletion feature).

There can be issues with poor PDF formatting, such as when all pages are linked
to the same resource. In such cases, dropping references to specific pages
becomes useless because there is only one source for all pages.

Cropping is an ineffective method for reducing the file size because it only
adjusts the viewboxes and not the external parts of the source image. Therefore,
the content that is no longer visible will still be present in the PDF.
