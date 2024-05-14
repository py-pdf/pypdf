# Merging PDF files

## Basic Example

```python
from pypdf import PdfWriter

merger = PdfWriter()

for pdf in ["file1.pdf", "file2.pdf", "file3.pdf"]:
    merger.append(pdf)

merger.write("merged-pdf.pdf")
merger.close()
```

For more details, see an excellent answer on
[StackOverflow](https://stackoverflow.com/questions/3444645/merge-pdf-files)
by Paul Rooney.

## Showing more merging options

```python
from pypdf import PdfWriter

merger = PdfWriter()

input1 = open("document1.pdf", "rb")
input2 = open("document2.pdf", "rb")
input3 = open("document3.pdf", "rb")

# Add the first 3 pages of input1 document to output
merger.append(fileobj=input1, pages=(0, 3))

# Insert the first page of input2 into the output beginning after the second page
merger.merge(position=2, fileobj=input2, pages=(0, 1))

# Append entire input3 document to the end of the output document
merger.append(input3)

# Write to an output PDF document
output = open("document-output.pdf", "wb")
merger.write(output)

# Close file descriptors
merger.close()
output.close()
```

## append

`append` has been slightly extended in `PdfWriter`. See [PdfWriter.append](../modules/PdfWriter.html#pypdf.PdfWriter.append) for more details.

### Examples

```python
# Append the first 10 pages of source.pdf
writer.append("source.pdf", (0, 10))

# Append the first and 10th page from reader and create an outline
writer.append(reader, "page 1 and 10", [0, 9])
```

During merging, the relevant named destination will also imported.

If you want to insert pages in the middle of the destination, use `merge` (which provides an insertion position).
You can insert the same page multiple times, if necessary even using a list-based syntax:

```python
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
previously named `field1` will now identified as `form1.field1` when calling
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

In order to prevent side effects between pages/objects and all objects linked cloning is done during the merge.

This process will be automatically applied if you use `PdfWriter.append/merge/add_page/insert_page`.
If you want to clone an object before attaching it "manually", use the `clone` method of any *PdfObject*:

```python
cloned_object = object.clone(writer)
```

If you try to clone an object already belonging to the writer, it will return the same object:

```python
assert cloned_object == object.clone(writer)
```

The same holds true if you try to clone an object twice. It will return the previously cloned object:

```python
assert object.clone(writer) == object.clone(writer)
```

Please note that if you clone an object, you will clone all the objects below as well,
including the objects pointed by *IndirectObject*. Due to this, if you clone a page that
includes some articles (`"/B"`), not only the first article, but also all the chained articles
and the pages where those articles can be read will be copied.
This means that you may copy lots of objects which will be saved in the output PDF as well.

In order to prevent this, you can provide the list of fields in the dictionaries to be ignored:

```python
new_page = writer.add_page(reader.pages[0], excluded_fields=["/B"])
```

### Merging rotated pages

If you are working with rotated pages, you might want to call `transfer_rotation_to_content()` on the page
before merging to avoid wrongly rotated results:

```python
for page in writer.pages:
    if page.rotation != 0:
        page.transfer_rotation_to_content()
    page.merge_page(background, over=False)
```
