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

```{testcode}
from pypdf import PdfReader

reader = PdfReader("example.pdf")

for page in reader.pages:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            obj = annotation.get_object()
            print({"subtype": obj["/Subtype"], "location": obj["/Rect"]})
```

```{testoutput}
:hide:

{'subtype': '/Highlight', 'location': [376.771, 406.213, 413.78, 422.506]}
{'subtype': '/Popup', 'location': [596, 330.026, 780, 422.026]}
{'subtype': '/FileAttachment', 'location': [88.2923, 210.633, 95.2923, 227.633]}
{'subtype': '/Stamp', 'location': [145.117, 188.132, 227.806, 254.997]}
{'subtype': '/Popup', 'location': [612, 631.925, 816, 745.925]}
{'subtype': '/Text', 'location': [334.863, 777.445, 358.863, 801.445]}
{'subtype': '/Popup', 'location': [596, 709.445, 780, 801.445]}
```

Examples of reading three of the most common annotations:

## Text

```{testcode}
from pypdf import PdfReader

reader = PdfReader("example.pdf")

for page in reader.pages:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            subtype = annotation.get_object()["/Subtype"]
            if subtype == "/Text":
                print(annotation.get_object()["/Contents"])
```

```{testoutput}
:hide:

Text comment
```

## Highlights

```{testcode}
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

```{testcode}
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
