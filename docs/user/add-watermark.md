# Adding a Stamp or Watermark to a PDF

Adding stamps or watermarks are two common ways to manipulate PDF files.
A stamp is adding something on top of the document, a watermark is in the
background of the document.

## Stamp (Overlay) / Watermark (Underlay)

The process of stamping and watermarking is the same, you just need to set `over` parameter to `True` for stamping and `False` for watermarking.

You can use `merge_page()` if you don't need to transform the stamp:

```python
from pypdf import PdfReader, PdfWriter

stamp = PdfReader("bg.pdf").pages[0]
writer = PdfWriter(clone_from="source.pdf")
for page in writer.pages:
    page.merge_page(stamp, over=False)  # here set to False for watermarking

writer.write("out.pdf")
```

Otherwise use `merge_transformed_page()` with `Transformation()` if you need to translate, rotate, scale, etc. the stamp before merging it to the content page.

```python
from pathlib import Path
from typing import List, Union

from pypdf import PdfReader, PdfWriter, Transformation


def stamp(
    content_pdf: Union[Path, str],
    stamp_pdf: Union[Path, str],
    pdf_result: Union[Path, str],
    page_indices: Union[None, List[int]] = None,
):
    stamp_page = PdfReader(stamp_pdf).pages[0]

    writer = PdfWriter()
    # page_indices can be a List(array) of page, tuples are for range definition
    reader = PdfReader(content_pdf)
    writer.append(reader, pages=page_indices)

    for content_page in writer.pages:
        content_page.merge_transformed_page(
            stamp_page,
            Transformation().scale(0.5),
        )

    writer.write(pdf_result)


stamp("example.pdf", "stamp.pdf", "out.pdf")
```

If you are experiencing wrongly rotated watermarks/stamps, try to use
`transfer_rotation_to_content()` on the corresponding pages beforehand
to fix the page boxes.

Example of stamp:
![stamp.png](stamp.png)

Example of watermark:
![watermark.png](watermark.png)


## Stamping images directly

The above code only works for stamps that are already in PDF format.
However, you can easily convert an image to PDF image using
[Pillow](https://pypi.org/project/Pillow/).


```python
from io import BytesIO
from pathlib import Path
from typing import List, Union

from PIL import Image
from pypdf import PageRange, PdfReader, PdfWriter, Transformation


def image_to_pdf(stamp_img: Union[Path, str]) -> PdfReader:
    img = Image.open(stamp_img)
    img_as_pdf = BytesIO()
    img.save(img_as_pdf, "pdf")
    return PdfReader(img_as_pdf)


def stamp_img(
    content_pdf: Union[Path, str],
    stamp_img: Union[Path, str],
    pdf_result: Union[Path, str],
    page_indices: Union[PageRange, List[int], None] = None,
):
    # Convert the image to a PDF
    stamp_pdf = image_to_pdf(stamp_img)

    # Then use the same stamp code from above
    stamp_page = stamp_pdf.pages[0]

    writer = PdfWriter()

    reader = PdfReader(content_pdf)
    writer.append(reader, pages=page_indices)
    for content_page in writer.pages:
        content_page.merge_transformed_page(
            stamp_page,
            Transformation(),
        )

    with open(pdf_result, "wb") as fp:
        writer.write(fp)


stamp_img("example.pdf", "example.png", "out.pdf")
```
