# Adding a Stamp/Watermark to a PDF

Adding stamps or watermarks are two common ways to manipulate PDF files.
A stamp is adding something on top of the document, a watermark is in the
background of the document.

In both cases you might want to ensure that the mediabox/cropbox of the original
content stays the same.

## Stamp (Overlay)

```python
from PyPDF2 import PdfWriter, PdfReader


def stamp(content_page, image_page):
    """Put the image over the content"""
    # Note that this modifies the content_page in-place!
    content_page.merge_page(image_page)
    return content_page


# Read the pages
reader_content = PdfReader("content.pdf")
reader_image = PdfReader("image.pdf")

# Modify it
modified = stamp(reader_content.pages[0], reader_image.pages[0])

# Create the new document
writer = PdfWriter()
writer.add_page(modified)
with open("out-stamp.pdf", "wb") as fp:
    writer.write(fp)
```

![stamp.png](stamp.png)

## Watermark (Underlay)

```python
from PyPDF2 import PdfWriter, PdfReader


def watermark(content_page, image_page):
    """Put the image under the content"""
    # Note that this modifies the image_page in-place!
    image_page.merge_page(content_page)
    return image_page


# Read the pages
reader_content = PdfReader("content.pdf")
reader_image = PdfReader("image.pdf")

# Modify it
modified = stamp(reader_content.pages[0], reader_image.pages[0])

# Create the new document
writer = PdfWriter()
writer.add_page(modified)
with open("out-watermark.pdf", "wb") as fp:
    writer.write(fp)
```

![watermark.png](watermark.png)
