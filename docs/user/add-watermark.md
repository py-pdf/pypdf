# Adding a Stamp/Watermark to a PDF

Adding stamps or watermarks are two common ways to manipulate PDF files.
A stamp is adding something on top of the document, a watermark is in the
background of the document.

## Stamp (Overlay) / Watermark (Underlay)

The process of stamping and watermarking is the same, you just need to set `over` parameter to `True` for stamping and `False` for watermarking.

You can use `merge_page()` if you don't need to transform the stamp:

```python
from pypdf import PdfWriter, PdfReader

stamp = PdfReader("bg.pdf").pages[0]
writer = PdfWriter(clone_from="source.pdf")
for page in writer.pages:
    page.merge_page(stamp, over=False)  # here set to False for watermarking

writer.write("out.pdf")
```

Else use `merge_transformed_page()` with `Transformation()` if you need to translate, rotate, scale, etc. the stamp before merging it to the content page.

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
    # page_indices can be a List(array) of page, tuples are for range definition
    writer.append(content, pages=None if page_indices == "ALL" else page_indices)

    for content_page in writer.pages:
        content_page.merge_transformed_page(
            stamp_page,
            Transformation().scale(0.5),
        )

    writer.write(pdf_result)
```

If you are experiencing wrongly rotated watermarks/stamps, try to use `transfer_rotation_to_content()` on the corresponding pages beforehand to fix the page boxes.

Example of stamp:
![stamp.png](stamp.png)

Example of watermark:
![watermark.png](watermark.png)
