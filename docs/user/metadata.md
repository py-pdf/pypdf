# Metadata

## Reading metadata

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")

meta = reader.metadata

# All of the following could be None!
print(meta.title)
print(meta.author)
print(meta.subject)
print(meta.creator)
print(meta.producer)
print(meta.creation_date)
print(meta.modification_date)
```

## Writing metadata

```python
from datetime import datetime
from pypdf import PdfReader, PdfWriter

reader = PdfReader("example.pdf")
writer = PdfWriter()

# Add all pages to the writer
for page in reader.pages:
    writer.add_page(page)

# If you want to add the old metadata, include these two lines
if reader.metadata is not None:
    writer.add_metadata(reader.metadata)

# Format the current date and time for the metadata
utc_time = "-05'00'"  # UTC time optional
time = datetime.now().strftime(f"D\072%Y%m%d%H%M%S{utc_time}")

# Add the new metadata
writer.add_metadata(
    {
        "/Author": "Martin",
        "/Producer": "Libre Writer",
        "/Title": "Title",
        "/Subject": "Subject",
        "/Keywords": "Keywords",
        "/CreationDate": time,
        "/ModDate": time,
        "/Creator": "Creator",
        "/CustomField": "CustomField",
    }
)

# Save the new PDF to a file
with open("meta-pdf.pdf", "wb") as f:
    writer.write(f)
```

## Updating metadata

```python
from pypdf import PdfReader, PdfWriter

writer = PdfWriter(clone_from="example.pdf")

# Change some values.
writer.add_metadata(
    {
        "/Author": "Martin",
        "/Producer": "Libre Writer",
        "/Title": "Title",
    }
)

# Save the new PDF to a file
with open("meta-pdf.pdf", "wb") as f:
    writer.write(f)
```
