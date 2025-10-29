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

reader = PdfReader("../resources/commented.pdf")

for page in reader.pages:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            obj = annotation.get_object()
            print({"subtype": obj["/Subtype"], "location": obj["/Rect"]})
```

```{testoutput}
:hide:

{'subtype': '/Text', 'location': [270.75, 596.25, 294.75, 620.25]}
{'subtype': '/Popup', 'location': [294.75, 446.25, 494.75, 596.25]}
{'subtype': '/Highlight', 'location': [176, 557, 203, 568]}
{'subtype': '/Popup', 'location': [202, 413, 402, 563]}
{'subtype': '/Text', 'location': [188.625, 485.25, 212.625, 509.25]}
{'subtype': '/Popup', 'location': [212.625, 335.25, 412.625, 485.25]}
```

Examples of reading three of the most common annotations:

## Text

```{testcode}
from pypdf import PdfReader

reader = PdfReader("../resources/commented.pdf")

for page in reader.pages:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            subtype = annotation.get_object()["/Subtype"]
            if subtype == "/Text":
                print(annotation.get_object()["/Contents"])
```

```{testoutput}
:hide:

Note in second paragraph
note over "kinds"

Like in "kinds of people"

----------

Umlaut: äöüß
```

## Highlights

```{testcode}
from pypdf import PdfReader

reader = PdfReader("../resources/commented.pdf")

for page in reader.pages:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            subtype = annotation.get_object()["/Subtype"]
            if subtype == "/Highlight":
                coords = annotation.get_object()["/QuadPoints"]
                x1, y1, x2, y2, x3, y3, x4, y4 = coords
                print(f"{x1=}, {y1=}, {x2=}, {y2=}, {x3=}, {y3=}, {x4=}, {y4=}")
```

```{testoutput}
:hide:

x1=176, y1=568, x2=203, y2=568, x3=176, y3=557, x4=203, y4=557
```

## Attachments

```{testcode}
from pypdf import PdfReader

reader = PdfReader("../resources/attachment.pdf")

for page in reader.pages:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            subtype = annotation.get_object()["/Subtype"]
            if subtype == "/FileAttachment":
                fileobj = annotation.get_object()["/FS"]
                name = fileobj["/F"]
                data = fileobj["/EF"]["/F"].get_data()
                print(f"{name=} {len(data)=}")
```

Output

```{testoutput}
:hide:

name='jpeg.pdf' len(data)=100898
```
