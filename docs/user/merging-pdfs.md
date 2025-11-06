# Merging PDF files

## Basic Example

```{testsetup}
pypdf_test_setup("user/merging-pdfs", {
    "example.pdf": "../resources/example.pdf",
    "hello-world.pdf": "../resources/hello-world.pdf",
    "jpeg.pdf": "../resources/jpeg.pdf",
    "GeoBase_NHNC1_Data_Model_UML_EN.pdf": "../resources/GeoBase_NHNC1_Data_Model_UML_EN.pdf",
    "Seige_of_Vicksburg_Sample_OCR.pdf": "../resources/Seige_of_Vicksburg_Sample_OCR.pdf",
    "two-different-pages.pdf": "../resources/two-different-pages.pdf",
})
```

```{testcode}
from pypdf import PdfWriter

merger = PdfWriter()

for pdf in ["example.pdf", "hello-world.pdf", "jpeg.pdf"]:
    merger.append(pdf)

merger.write("out-basic.pdf")
```

For more details, see an excellent answer on
[StackOverflow](https://stackoverflow.com/questions/3444645/merge-pdf-files)
by Paul Rooney.

````{note}
Dealing with large PDF files might reach the recursion limit of the current
Python interpreter. In these cases, increasing the limit might help:

```{testcode}
import sys

# Example: Increase the current limit by factor 5.
sys.setrecursionlimit(sys.getrecursionlimit() * 5)
```
````

## Showing more merging options

```{testcode}
from pypdf import PdfWriter

merger = PdfWriter()

with (
    open("Seige_of_Vicksburg_Sample_OCR.pdf", "rb") as input1,
    open("two-different-pages.pdf", "rb") as input2,
    open("example.pdf", "rb") as input3
):
    # Add the first 3 pages of input1 document to output
    merger.append(fileobj=input1, pages=(0, 3))

    # Insert the first page of input2 into the output beginning after the second page
    merger.merge(position=2, fileobj=input2, pages=(0, 1))

    # Append entire input3 document to the end of the output document
    merger.append(input3)

    # Write to an output PDF document
    merger.write("out-advanced.pdf")
```

## append

`append` has been slightly extended in `PdfWriter`. See {func}`~pypdf.PdfWriter.append` for more details.

### Examples

```{testcode}
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()

source_file_name = "GeoBase_NHNC1_Data_Model_UML_EN.pdf"

# Append the first 10 pages from pdf file
writer.append(source_file_name, (0, 10))

reader = PdfReader(source_file_name)

# Append the first and 10th page from reader and create an outline
writer.append(reader, "page 1 and 10", [0, 9])
```

During merging, the relevant named destination will also be imported.

If you want to insert pages in the middle of the destination, use `merge` (which provides an insertion position).
You can insert the same page multiple times, if necessary, even using a list-based syntax:

```{testcode}
# Insert pages 2 and 3, with page 1 before, between, and after
writer.append(reader, [0, 1, 0, 2, 0])
```

## add_page / insert_page

It is recommended to use `append` or `merge` instead.

## Merging forms

When merging forms, some form fields may have the same names, preventing access to some data.

A grouping field should be added before adding the source PDF to prevent that.
The original fields will be identified by adding the group name.

For example, after calling `reader.add_form_topname("form1")`, the field
previously named `field1` is now identified as `form1.field1` when calling
`reader.get_form_text_fields(True)` or `reader.get_fields()`.

After that, you can append the input PDF completely or partially using
`writer.append` or `writer.merge`. If you insert a set of pages, only those
fields will be listed.

## reset_translation

During cloning, if an object has been already cloned, it will not be cloned again, and a pointer
to this previously cloned object is returned instead. Because of that, if you add/merge a page that has
already been added, the same object will be added the second time. If you modify any of these two pages later,
both pages can be modified independently.

To reset, call  `writer.reset_translation(reader)`.

## Advanced cloning

To prevent side effects between pages/objects and all objects linked cloning is done during the merge.

This process will be automatically applied if you use `PdfWriter.append/merge/add_page/insert_page`.
If you want to clone an object before attaching it "manually", use the `clone` method of any *PdfObject*:

```{testcode}
from pypdf.generic import NameObject, NumberObject, StreamObject

stream_object = StreamObject()

cloned_object = stream_object.clone(writer)
```

If you try to clone an object already belonging to the writer, it will return the same object:

```{testcode}
assert cloned_object == stream_object.clone(writer)
```

The same holds true if you try to clone an object twice. It will return the previously cloned object:

```{testcode}
assert stream_object.clone(writer) == stream_object.clone(writer)
```

Please note that if you clone an object, you will clone all the objects below as well,
including the objects pointed by *IndirectObject*. Due to this, if you clone a page that
includes some articles (`"/B"`), not only the first article, but also all the chained articles
and the pages where those articles can be read will be copied.
This means that you may copy lots of objects which will be saved in the output PDF as well.

To prevent this, you can provide the list of fields in the dictionaries to be ignored:

```{testcode}
new_page = writer.add_page(reader.pages[0], excluded_keys=["/B"])
```

### Merging rotated pages

If you are working with rotated pages, you might want to call {func}`~pypdf._page.PageObject.transfer_rotation_to_content` on the page
before merging to avoid wrongly rotated results:

```{testcode}
background = PdfReader("jpeg.pdf").pages[0]

for page in writer.pages:
    if page.rotation != 0:
        page.transfer_rotation_to_content()
    page.merge_page(background, over=False)
```
