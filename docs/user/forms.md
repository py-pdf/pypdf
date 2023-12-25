# Interactions with PDF Forms

## Reading form fields

```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")
fields = reader.get_form_text_fields()
fields == {"key": "value", "key2": "value2"}

# You can also get all fields:
fields = reader.get_fields()
```

## Filling out forms

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("form.pdf")
writer = PdfWriter()

page = reader.pages[0]
fields = reader.get_fields()

writer.append(reader)

writer.update_page_form_field_values(
    writer.pages[0],
    {"fieldname": "some filled in text"},
    auto_regenerate=False,
)

# write "output" to pypdf-output.pdf
with open("filled-out.pdf", "wb") as output_stream:
    writer.write(output_stream)
```

Generally speaking, you will always want to use `auto_regenerate=False`. The
parameter is `True` by default for legacy compatibility, but this flags the PDF
Viewer to recompute the field's rendering, and may trigger a "save changes"
dialog for users who open the generated PDF.

## A note about form fields and annotations

The PDF form stores form fields as annotations with the subtype "\Widget". This means that the following two blocks of code will give fairly similar results:

```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")
fields = reader.get_fields()
```

```python
from pypdf import PdfReader
from pypdf.constants import AnnotationDictionaryAttributes

reader = PdfReader("form.pdf")
fields = []
for page in reader.pages:
    for annot in page.annotations:
        annot = annot.get_object()
        if annot[AnnotationDictionaryAttributes.Subtype] == "/Widget":
            fields.append(annot)
```

However, while similar, there are some very important differences between the two above blocks of code. Most importantly, the first block will return a list of Field objects, where as the second will return more generic dictionary-like objects. The objects lists will *mostly* reference the same object in the underlying PDF, meaning you'll find that `obj_taken_fom_first_list.indirect_reference == obj_taken_from _second_list.indirect_reference`. Field objects are generally more ergonomic, as the exposed data can be access via clearly named properties. However, the more generic dictionary-like objects will contain data that the Field object does not expose, such as the Rect (the widget's position on the page). So, which to use will depend on your use case.

However, it's also important to note that the two lists do not *always* refer to the same underlying PDF objects. For example, if the form contains radio buttons, you will find that `reader.get_fields()` will get the parent object (the group of radio buttons) whereas `page.annotations` will return all the child objects (the individual radio buttons).
