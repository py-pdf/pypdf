# Metadata

## Reading metadata

```python
from PyPDF2 import PdfReader

reader = PdfReader("example.pdf")

info = reader.getDocumentInfo()

print(reader.numPages)

# All of the following could be None!
print(info.author)
print(info.creator)
print(info.producer)
print(info.subject)
print(info.title)
```

## Writing metadata

```python
from PyPDF2 import PdfReader, PdfWriter

reader = PdfReader("example.pdf")
writer = PdfWriter()

# Add all pages to the writer
for i in range(reader.numPages):
    page = reader.pages[i]
    writer.addPage(page)

# Add the metadata
writer.addMetadata(
    {
        "/Author": "Martin",
        "/Producer": "Libre Writer",
    }
)

# Save the new PDF to a file
with open("meta-pdf.pdf", "wb") as f:
    writer.write(f)
```
