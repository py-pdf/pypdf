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
