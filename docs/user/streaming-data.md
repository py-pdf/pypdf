# Streaming Data with PyPDF2

In some cases you might want to avoid saving things explicitly as a file
to disk, e.g. when you want to store the PDF in a database or AWS S3.

PyPDF2 supports streaming data to a file-like object and here is how.

```python
from io import BytesIO

# Prepare example
with open("example.pdf", "rb") as fh:
    bytes_stream = BytesIO(fh.read())

# Read from bytes_stream
reader = PdfFileReader(bytes_stream)

# Write to bytes_stream
writer = PdfFileWriter()
with BytesIO() as bytes_stream:
    writer.write(bytes_stream)
```
