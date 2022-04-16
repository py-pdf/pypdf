# Reading PDF Annotations

PDF 1.7 defines 25 different annotation types:

* Text
* Link
* FreeText
* Line, Square, Circle, Polygon, PolyLine, Highlight, Underline, Squiggly, StrikeOut
* Stamp, Caret, Ink
* Popup
* FileAttachment
* Sound, Movie
* Widget, Screen
* PrinterMark
* TrapNet
* Watermark
* 3D

Reading the most common ones is described here.

## Text

```python
from PyPDF2 import PdfFileReader

reader = PdfFileReader("example.pdf")

for page in reader.pages:
    if "/Annots" in page:
        for annot in page["/Annots"]:
            subtype = annot.getObject()["/Subtype"]
            if subtype == "/Text":
                print(annot.getObject()["/Contents"])
```

## Highlights

```python
from PyPDF2 import PdfFileReader

reader = PdfFileReader("commented.pdf")

for page in reader.pages:
    if "/Annots" in page:
        for annot in page["/Annots"]:
            subtype = annot.getObject()["/Subtype"]
            if subtype == "/Highlight":
                coords = annot.getObject()["/QuadPoints"]
                x1, y1, x2, y2, x3, y3, x4, y4 = coords
```

## Attachments

```python
from PyPDF2 import PdfFileReader

reader = PdfFileReader("example.pdf")

attachments = {}
for page in reader.pages:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            subtype = annot.getObject()["/Subtype"]
            if subtype == "/FileAttachment":
                fileobj = annotobj["/FS"]
                attachments[fileobj["/F"]] = fileobj["/EF"]["/F"].getData()
```
