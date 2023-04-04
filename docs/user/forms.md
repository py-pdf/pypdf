# Interactions with PDF Forms

## Reading form fields

```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")
fields = reader.get_form_text_fields()
fields == {"key": "value", "key2": "value2"}
```

## Filling out forms

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("form.pdf")
writer = PdfWriter()

writer.append_pages_from_reader(reader)
writer.update_page_form_field_values(
    writer.pages[0], {"fieldname": "some filled in text"}
)

# write "output" to pypdf-output.pdf
with open("filled-out.pdf", "wb") as output_stream:
    writer.write(output_stream)
```
