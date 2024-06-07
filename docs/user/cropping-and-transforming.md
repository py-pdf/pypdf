# Cropping and Transforming PDFs

> **Notice**: Just because content is no longer visible, it is not gone.
> Cropping works by adjusting the viewbox. That means content that was cropped
> away can still be restored.

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("example.pdf")
writer = PdfWriter()

# Add page 1 from reader to output document, unchanged.
writer.add_page(reader.pages[0])

# Add page 2 from reader, but rotated clockwise 90 degrees.
writer.add_page(reader.pages[1].rotate(90))

# Add page 3 from reader, but crop it to half size.
page3 = reader.pages[2]
page3.mediabox.upper_right = (
    page3.mediabox.right / 2,
    page3.mediabox.top / 2,
)
writer.add_page(page3)

# Add some JavaScript to launch the print window on opening this PDF.
# The password dialog may prevent the print dialog from being shown,
# comment the encryption lines, if that's the case, to try this out.
# https://opensource.adobe.com/dc-acrobat-sdk-docs/library/jsapiref/index.html
writer.add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")

# Write to pypdf-output.pdf.
with open("pypdf-output.pdf", "wb") as fp:
    writer.write(fp)
```

## Page rotation

The most typical rotation is a clockwise rotation of the page by multiples of
90 degrees. That is done when the orientation of the page is wrong. You can
do that with the [`rotate` method](https://pypdf.readthedocs.io/en/latest/modules/PageObject.html#pypdf._page.PageObject.rotate)
of the `PageObject` class:

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

writer.add_page(reader.pages[0])
writer.pages[0].rotate(90)

with open("output.pdf", "wb") as fp:
    writer.write(fp)
```

The rotate method is typically preferred over the `page.add_transformation(Transformation().rotate())`
method, because `rotate` will ensure that the page is still in the mediabox /
cropbox. The transformation object operates on the coordinates of the pages
contents and does not change the mediabox or cropbox.



## Plain Merge

![](plain-merge.png)

is the result of

```python
from pypdf import PdfReader, PdfWriter, Transformation

# Get the data
reader_base = PdfReader("labeled-edges-center-image.pdf")
page_base = reader_base.pages[0]

reader = PdfReader("box.pdf")
page_box = reader.pages[0]

page_base.merge_page(page_box)

# Write the result back
writer = PdfWriter()
writer.add_page(page_base)
with open("merged-foo.pdf", "wb") as fp:
    writer.write(fp)
```

## Merge with Rotation

![](merge-45-deg-rot.png)

```python
from pypdf import PdfReader, PdfWriter, Transformation

# Get the data
reader_base = PdfReader("labeled-edges-center-image.pdf")
page_base = reader_base.pages[0]

reader = PdfReader("box.pdf")
page_box = reader.pages[0]

# Apply the transformation
transformation = Transformation().rotate(45)
page_box.add_transformation(transformation)
page_base.merge_page(page_box)

# Write the result back
writer = PdfWriter()
writer.add_page(page_base)
with open("merged-foo.pdf", "wb") as fp:
    writer.write(fp)
```

If you add the expand parameter:

```python
transformation = Transformation().rotate(45)
page_box.add_transformation(transformation)
page_base.merge_page(page_box, expand=True)
```

you get:

![](merge-rotate-expand.png)

Alternatively, you can move the merged image a bit to the right by using

```python
op = Transformation().rotate(45).translate(tx=50)
```

![](merge-translated.png)


## Scaling

pypdf offers two ways to scale: The page itself and the contents on a page.
Typically, you want to combine both.

![](scaling.png)

### Scaling a Page (the Canvas)

```python
from pypdf import PdfReader, PdfWriter

# Read the input
reader = PdfReader("resources/side-by-side-subfig.pdf")
page = reader.pages[0]

# Scale
page.scale_by(0.5)

# Write the result to a file
writer = PdfWriter()
writer.add_page(page)
writer.write("out.pdf")
```

If you wish to have more control, you can adjust the various page boxes
directly:

```python
from pypdf.generic import RectangleObject

mb = page.mediabox

page.mediabox = RectangleObject((mb.left, mb.bottom, mb.right, mb.top))
page.cropbox = RectangleObject((mb.left, mb.bottom, mb.right, mb.top))
page.trimbox = RectangleObject((mb.left, mb.bottom, mb.right, mb.top))
page.bleedbox = RectangleObject((mb.left, mb.bottom, mb.right, mb.top))
page.artbox = RectangleObject((mb.left, mb.bottom, mb.right, mb.top))
```

### Scaling the content

The content is scaled towards the origin of the coordinate system. Typically,
that is the lower-left corner.

```python
from pypdf import PdfReader, PdfWriter, Transformation

# Read the input
reader = PdfReader("resources/side-by-side-subfig.pdf")
page = reader.pages[0]

# Scale
op = Transformation().scale(sx=0.7, sy=0.7)
page.add_transformation(op)

# Write the result to a file
writer = PdfWriter()
writer.add_page(page)
writer.write("out-pg-transform.pdf")
```

### pypdf._page.MERGE_CROP_BOX

`pypdf<=3.4.0` used to merge the other page with `trimbox`.

`pypdf>3.4.0` changes this behavior to `cropbox`.

In case anybody has good reasons to use/expect `trimbox`, please let me know via
info@martin-thoma.de or via https://github.com/py-pdf/pypdf/pull/1622
In the mean time, you can add the following code to get the old behavior:

```python
pypdf._page.MERGE_CROP_BOX = "trimbox"
```

# Transforming several copies of the same page

We have designed the following business card (A8 format) to advertise our new startup.

![](nup-source.png)

We would like to copy this card sixteen times on an A4 page, to print it, cut it, and give it to all our friends. Having learned about the ``merge_page()`` method and the ``Transformation`` class, we run the following code. Notice that we had to tweak the media box of the source page to extend it, which is already a dirty hack (in this case).

```python
from pypdf import PaperSize, PdfReader, PdfWriter, Transformation

# Read source file
reader = PdfReader("nup-source.pdf")
sourcepage = reader.pages[0]

# Create a destination file, and add a blank page to it
writer = PdfWriter()
destpage = writer.add_blank_page(width=PaperSize.A4.height, height=PaperSize.A4.width)

# Extend source page mediabox
sourcepage.mediabox = destpage.mediabox

# Copy source page to destination page, several times
for x in range(4):
    for y in range(4):
        # Translate page
        sourcepage.add_transformation(
            Transformation().translate(
                x * PaperSize.A8.height,
                y * PaperSize.A8.width,
            )
        )
        # Merge translated page
        destpage.merge_page(sourcepage)

# Write file
with open("nup-dest1.pdf", "wb") as fp:
    writer.write(fp)
```

And the result is… unexpected.

![](nup-dest1.png)

The problem is that, having run ``add.transformation()`` several times on the *same* source page, those transformations add up: for instance, the sixteen transformations are applied to the last copy of the source page, so most of the business cards are *outside* the destination page.

We need a way to merge a transformed page, *without* modifying the source page. Here comes ``merge_transformed_page()``. With this method:
- we no longer need the media box hack of our first try;
- transformations are only applied *once*.

```python
from pypdf import PaperSize, PdfReader, PdfWriter, Transformation

# Read source file
reader = PdfReader("nup-source.pdf")
sourcepage = reader.pages[0]

# Create a destination file, and add a blank page to it
writer = PdfWriter()
destpage = writer.add_blank_page(width=PaperSize.A4.height, height=PaperSize.A4.width)

# Copy source page to destination page, several times
for x in range(4):
    for y in range(4):
        destpage.merge_transformed_page(
            sourcepage,
            Transformation().translate(
                x * sourcepage.mediabox.width,
                y * sourcepage.mediabox.height,
            ),
        )

# Write file
with open("nup-dest2.pdf", "wb") as fp:
    writer.write(fp)
```

We get the expected result.

![](nup-dest2.png)

There is still some work to do, for instance to insert margins between and around cards, but this is left as an exercise for the reader…
