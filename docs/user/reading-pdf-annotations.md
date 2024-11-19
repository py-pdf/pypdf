# Reading PDF Annotations

PDF 2.0 defines the following annotation types:

* Text
* Link
* FreeText
* Line
* Square
* Circle
* Polygon
* PolyLine
* Highlight
* Underline
* Squiggly
* StrikeOut
* Caret
* Stamp
* Ink
* Popup
* FileAttachment
* Sound
* Movie
* Screen
* Widget
* PrinterMark
* TrapNet
* Watermark
* 3D
* Redact
* Projection
* RichMedia

In general, annotations can be read like this:

```python
from pypdf import PdfReader

reader = PdfReader("annotated.pdf")

for page in reader.pages:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            obj = annotation.get_object()
            print({"subtype": obj["/Subtype"], "location": obj["/Rect"]})
```

Examples of reading three of the most common annotations:

## Text

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")

for page in reader.pages:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            subtype = annotation.get_object()["/Subtype"]
            if subtype == "/Text":
                print(annotation.get_object()["/Contents"])
```

## Highlights

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")

for page in reader.pages:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            subtype = annotation.get_object()["/Subtype"]
            if subtype == "/Highlight":
                coords = annotation.get_object()["/QuadPoints"]
                x1, y1, x2, y2, x3, y3, x4, y4 = coords
```

## Attachments

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")

attachments = {}
for page in reader.pages:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            subtype = annotation.get_object()["/Subtype"]
            if subtype == "/FileAttachment":
                fileobj = annotation.get_object()["/FS"]
                attachments[fileobj["/F"]] = fileobj["/EF"]["/F"].get_data()
```
