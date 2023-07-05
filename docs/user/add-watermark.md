# Adding a Stamp/Watermark to a PDF

Adding stamps or watermarks are two common ways to manipulate PDF files.
A stamp is adding something on top of the document, a watermark is in the
background of the document.

## Stamp (Overlay)

Using the ``Transformation()`` class, one can translate, rotate, scale, etc. the stamp before merging it to the content page.

```python
from pathlib import Path
from typing import Union, Literal, List

from pypdf import PdfWriter, PdfReader


def stamp(
    content_pdf: Path,
    stamp_pdf: Path,
    pdf_result: Path,
    page_indices: Union[Literal["ALL"], List[int]] = "ALL",
):
    stamp_page = PdfReader(stamp_pdf).pages[0]

    writer = PdfWriter()

    reader = PdfReader(content_pdf)
    if page_indices == "ALL":
        page_indices = list(range(0, len(reader.pages)))
    for index in page_indices:
        writer.append(reader.pages[index])
    for content_page in writer.pages:
        content_page.merge_transformed_page(
            stamp_page,
            Transformation(),
        )

    with open(pdf_result, "wb") as fp:
        writer.write(fp)
```

![stamp.png](stamp.png)

## Watermark (Underlay)

To merge the watermark *under* the content, use the argument ``over=False`` of the method ``merge_transformed_page()``.

Once again, watermark size and position (and more) can be customized using the ``Transformation()`` class.

```python
from pathlib import Path
from typing import Union, Literal, List

from pypdf import PdfWriter, PdfReader, Transformation


def watermark(
    content_pdf: Path,
    stamp_pdf: Path,
    pdf_result: Path,
    page_indices: Union[Literal["ALL"], List[int]] = "ALL",
):
    reader = PdfReader(content_pdf)
    if page_indices == "ALL":
        page_indices = range(len(reader.pages))

    writer = PdfWriter()
    watermark_page = PdfReader(stamp_pdf).pages[0]
    for index in page_indices:
        writer.append(reader.pages[index])
    for content_page in writer.pages:
        content_page.merge_transformed_page(
            watermark_page,
            Transformation(),
            over=False,
        )

    with open(pdf_result, "wb") as fp:
        writer.write(fp)
```

![watermark.png](watermark.png)

## Stamping images not in PDF format

The above code only works for images that are already in PDF format. However, you can easilly convert an image to PDF image using [Pillow](https://pypi.org/project/Pillow/).

```python
from PIL import Image
from io import BytesIO
from pypdf import PdfWriter, PdfReader, Transformation

def stamp_img(
    content_pdf: Path,
    stamp_img: Path,
    pdf_result: Path,
    page_indices: Union[Literal["ALL"], List[int]] = "ALL",
):
    # Convert the image to a PDF
    img = Image.open(stamp_img)
    img_as_pdf = BytesIO()
    img.save(img_as_pdf, 'pdf')
    stamp_pdf = PdfReader(img_as_pdf)

    # Then use the same stamp code from above
    stamp_page = stamp_pdf.pages[0]

    writer = PdfWriter()

    reader = PdfReader(content_pdf)
    if page_indices == "ALL":
        page_indices = list(range(0, len(reader.pages)))
    for index in page_indices:
        writer.append(reader.pages[index])
    for content_page in writer.pages:
        content_page.merge_transformed_page(
            stamp_page,
            Transformation(),
        )

    with open(pdf_result, "wb") as fp:
        writer.write(fp)
```