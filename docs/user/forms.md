# Interactions with PDF Forms

## Reading form fields

```python
from PyPDF2 import PdfFileReader

reader = PdfFileReader("form.pdf")
fields = reader.getFormTextFields()
fields == {"key": "value", "key2": "value2"}
```

## Filling out forms

```python
from PyPDF2 import PdfFileReader, PdfFileWriter

reader = PdfFileReader("form.pdf")
writer = PdfFileWriter()

page = reader.pages[0]
fields = reader.getFields()

writer.addPage(page)

writer.updatePageFormFieldValues(
    writer.getPage(0), {"fieldname": "some filled in text"}
)

# write "output" to PyPDF2-output.pdf
with open("filled-out.pdf", "wb") as output_stream:
    writer.write(output_stream)
```
