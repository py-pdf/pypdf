# Adding PDF Annotations

## Attachments

```python
from PyPDF2 import PdfFileWriter

writer = PdfFileWriter()
writer.addBlankPage(width=200, height=200)

data = b"any bytes - typically read from a file"
writer.addAttachment("smile.png", data)

with open("output.pdf", "wb") as output_stream:
    writer.write(output_stream)
```
